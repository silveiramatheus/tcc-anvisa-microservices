from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import logging

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

with DAG(
    'anvisa_weekly_etl_pipeline',
    default_args=default_args,
    description='A weekly ETL pipeline for Anvisa medicines data',
    schedule_interval='0 0 * * 0',  # Every Sunday at midnight
    start_date=days_ago(1),
    catchup=False,
    tags=['anvisa', 'etl', 'medicines'],
) as dag:
    def task_extract(**kwargs):
        downloaded, file_path = download_check()
        # XCom (Cross-Communication): Passa dados para a próxima task
        kwargs['ti'].xcom_push(key='file_path', value=file_path)
        kwargs['ti'].xcom_push(key='downloaded', value=downloaded)
    
    def task_transform(**kwargs):
        ti = kwargs['ti']
        file_path = ti.xcom_pull(key='file_path', task_ids='extract_data')
        downloaded = ti.xcom_pull(key='downloaded', task_ids='extract_data')

        if not downloaded:
            print("No new data downloaded. Skipping transformation.")
            return None

        # Roda sua transformação
        df_original, df_validated = transform_data(file_path)
        
        # Como não dá pra passar DataFrame via XCom (é muito grande),
        # salvamos em Parquet temporário ou confiamos que a função de load vai rodar
        # Sugestão para manter simples: Chamar o Load direto aqui ou salvar em disco.
        # Vamos salvar em disco temporariamente para a task de load pegar.
        original_path = f"{config.DATA_DIR}/temp_original.pkl"
        validated_path = f"{config.DATA_DIR}/temp_validated.pkl"
        
        df_original.to_pickle(original_path)
        df_validated.to_pickle(validated_path)
    
    def task_load(**kwargs):
        ti = kwargs['ti']
        downloaded = ti.xcom_pull(key='downloaded', task_ids='extract_data')
        
        if not downloaded:
            print("Skipping load.")
            return

        import pandas as pd
        original_path = f"{config.DATA_DIR}/temp_original.pkl"
        validated_path = f"{config.DATA_DIR}/temp_validated.pkl"

        try:
            df_original = pd.read_pickle(original_path)
            df_validated = pd.read_pickle(validated_path)
            load_data(df_original, df_validated)
        except FileNotFoundError:
            print("Temp files not found. Maybe transformation failed?")
            raise

    # Definição dos Operadores do Airflow
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=task_extract,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=task_transform,
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=task_load,
    )

    extract_task >> transform_task >> load_task