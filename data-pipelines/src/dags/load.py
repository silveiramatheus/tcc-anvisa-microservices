from sqlalchemy import create_engine
import pandas as pd
import logging
import config

logger = logging.getLogger(__name__)

def load_data(df_original, df_validated):
    logger.info("Starting data loading process...")

    try:
        engine = create_engine(config.DATABASE_URL)
        logger.info(f"Database connection established to {config.DB_NAME} at {config.DB_HOST}:{config.DB_PORT}")
        df_original.to_sql(
            config.TABLE_NAME_ORIGINAL,
            con=engine,
            if_exists='replace',
            index=False,
            schema=config.DB_SCHEMA
        )
        logger.info(f"Original data loaded into table {config.TABLE_NAME_ORIGINAL} in schema {config.DB_SCHEMA}")

        if df_validated is not None and not df_validated.empty:
            df_validated.to_sql(
                config.TABLE_NAME_VALIDATED,
                con=engine,
                if_exists='replace',
                index=False,
                schema=config.DB_SCHEMA
            )
            logger.info(f"Validated data loaded into table {config.TABLE_NAME_VALIDATED} in schema {config.DB_SCHEMA}")
        
        logger.info("Data loading process completed successfully.")
        
    except Exception as e:
        logger.error(f"Error during data loading: {e}", exc_info=True)
        raise