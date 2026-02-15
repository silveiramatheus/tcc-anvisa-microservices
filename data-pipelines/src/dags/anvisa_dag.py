from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import timedelta
import pandas as pd
import logging
import os

from dags.extract import download_check
from dags.transform import transform_data
from dags.load import load_data
import config

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

SQL_PARAMS = {
    'table_staging': config.TABLE_NAME_STAGING,
    'table_dim_laboratory': config.TABLE_DIM_LAB,
    'table_dim_product': config.TABLE_DIM_PRODUCT,
    'table_fact_medication_presentation': config.TABLE_FACT_MEDICATION
}

with DAG(
    'anvisa_weekly_etl_pipeline',
    default_args=default_args,
    description='A weekly ETL pipeline for Anvisa medications data',
    schedule_interval='@weekly',
    start_date=days_ago(1),
    catchup=False,
    tags=['anvisa', 'etl', 'medications', 'upsert'],
    template_searchpath=[os.path.join(config.BASE_DIR, 'dags')]
) as dag:
    def task_extract(**kwargs):
        downloaded, file_path = download_check()
        kwargs['ti'].xcom_push(key='file_path', value=file_path)
        kwargs['ti'].xcom_push(key='downloaded', value=downloaded)
    
    def task_transform(**kwargs):
        ti = kwargs['ti']
        file_path = ti.xcom_pull(key='file_path', task_ids='extract_data')
        downloaded = ti.xcom_pull(key='downloaded', task_ids='extract_data')

        if not downloaded:
            print("No new data downloaded. Skipping transformation.")
            return None

        df_original, df_validated = transform_data(file_path)
        original_path = f"{config.DATA_DIR}/temp_original.pkl"
        validated_path = f"{config.DATA_DIR}/temp_validated.pkl"
        
        df_original.to_pickle(original_path)
        df_validated.to_pickle(validated_path)
    
    def task_load_staging(**kwargs):
        ti = kwargs['ti']
        status = ti.xcom_pull(task_ids='transform_data')
        
        if status == "skipped":
            print("Skipping load.")
            return

        original_path = f"{config.DATA_DIR}/temp_original.pkl"
        validated_path = f"{config.DATA_DIR}/temp_validated.pkl"

        try:
            df_original = pd.read_pickle(original_path)
            df_validated = pd.read_pickle(validated_path)
            load_data(df_original, df_validated)
        except FileNotFoundError:
            raise Exception("Temp files not found.")

    # Definição dos Operadores do Airflow
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=task_extract,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=task_transform,
    )

    load_staging_task = PythonOperator(
        task_id='load_to_staging',
        python_callable=task_load_staging,
    )

    upsert_dim_laboratory = SQLExecuteQueryOperator(
        task_id='upsert_dim_laboratory',
        conn_id='postgres_default', 
        sql='sql/upsert_dim_laboratory.sql',
        params=SQL_PARAMS
    )

    upsert_dim_product = SQLExecuteQueryOperator(
        task_id='upsert_dim_product',
        conn_id='postgres_default',
        sql='sql/upsert_dim_product.sql',
        params=SQL_PARAMS
    )

    upsert_fact_medication = SQLExecuteQueryOperator(
        task_id='upsert_fact_medication',
        conn_id='postgres_default',
        sql='sql/upsert_fact_medication.sql',
        params=SQL_PARAMS
    )

    truncate_staging_anvisa_medications = SQLExecuteQueryOperator(
        task_id='truncate_staging_anvisa_medications',
        conn_id='postgres_default',
        sql='sql/truncate_staging_anvisa_medications.sql',
        params=SQL_PARAMS
    )

    extract_task >> transform_task >> load_staging_task
    load_staging_task >> [upsert_dim_laboratory, upsert_dim_product]
    [upsert_dim_laboratory, upsert_dim_product] >> upsert_fact_medication
    upsert_fact_medication >> truncate_staging_anvisa_medications