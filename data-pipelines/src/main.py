import logging
import argparse
from dags.extract import download_check
from dags.transform import transform_data
from dags.load import load_data
import config
import os

config.setup_logging()

logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("="*50)
    logger.info("Starting the data pipeline...")
    logger.info("="*50)

    downloaded, file_path = download_check()
    if not downloaded:
        logger.info("No new data to process. Exiting pipeline.")
        return
    
    logger.info(f"Data downloaded successfully to {file_path}. Proceeding with transformation...")

    df_original, df_validated = transform_data(file_path)   

    if df_original is None:
        logger.error("Transformation failed. Exiting pipeline.")
        return
    
    try:
        debug_path = os.path.join(config.DATA_DIR, "cleaned_data.csv")
        df_validated.to_csv(debug_path, index=False, sep=';', encoding='utf-8')
        logger.info(f"DEBUG: Cleaned file saved to {debug_path} for inspection.")
    except Exception as e:
        logger.warning(f"Failed to save debug file: {e}")
    
    if skip_load:
        logger.info("Skipping data loading step as per user request.")
        try:
            output_original_path = os.path.join(config.DATA_DIR, "transformed_original.csv")
            output_validated_path = os.path.join(config.DATA_DIR, "transformed_validated.csv")

            df_original.to_csv(output_original_path, index=False, sep=",", encoding="utf-8")
            df_validated.to_csv(output_validated_path, index=False, sep=",", encoding="utf-8")
            logger.info(f"Transformed data saved to {output_original_path} and {output_validated_path}")
        
        except Exception as e:
            logger.error(f"Error saving transformed data: {e}", exc_info=True)

    else:
        logger.info("Loading data into the database...")
        try:
            load_data(df_original, df_validated)
            logger.info("Data loading completed successfully.")

        except Exception as e:
            logger.error(f"Error during data loading: {e}", exc_info=True)  
    
    logger.info("Completed the data pipeline successfully.")
    logger.info("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the data pipeline.")
    parser.add_argument('--skip-load', action='store_true', help="Skip the loading step to the database")
    args = parser.parse_args()
    
    skip_load = args.skip_load

    run_pipeline()