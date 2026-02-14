import logging
import argparse
import os
import config
from dags.extract import download_check
from dags.transform import transform_data
from dags.load import load_data

config.setup_logging()
logger = logging.getLogger(__name__)

def run_pipeline(skip_load=False, save_debug=False):
    logger.info("="*50)
    logger.info("Starting the data pipeline (ETL Service)...")
    logger.info("="*50)

    downloaded, file_path = download_check()
    if not downloaded:
        logger.info("No new data to process. Pipeline finished.")
        return
    
    logger.info(f"Processing file: {file_path}")
    df_original, df_validated = transform_data(file_path)   

    if df_original is None:
        logger.error("Transformation phase failed.")
        return
    
    if save_debug:
        try:
            debug_path = os.path.join(config.DATA_DIR, "debug_last_run.csv")
            df_validated.to_csv(debug_path, index=False, sep=';', encoding='utf-8')
            logger.info(f"DEBUG: Sample saved to {debug_path}")
        except Exception as e:
            logger.warning(f"Could not save debug file: {e}")
    
    if skip_load:
        logger.warning("SKIP_LOAD ACTIVE: Data was processed but NOT sent to the database.")
    else:
        logger.info(f"Connecting to database to load {len(df_validated)} rows...")
        try:
            load_data(df_original, df_validated)
            logger.info("Load phase completed successfully!")
            
            # os.remove(file_path) 
            
        except Exception as e:
            logger.error(f"Critical error during Load phase: {e}")
            return

    logger.info("="*50)
    logger.info("Pipeline Execution Finished.")
    logger.info("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anvisa Data Pipeline CLI")
    parser.add_argument('--skip-load', action='store_true', help="Do not load data into Postgres")
    parser.add_argument('--debug', action='store_true', help="Save a local CSV for inspection")
    
    args = parser.parse_args()
    run_pipeline(skip_load=args.skip_load, save_debug=args.debug)