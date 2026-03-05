import pandas as pd
import logging

logger = logging.getLogger(__name__)

COLUMNS_MAP = {
    "SUBSTÂNCIA": "substance",
    "CNPJ": "cnpj",
    "LABORATÓRIO": "laboratory",
    "CÓDIGO GGREM": "ggrem_code",
    "REGISTRO": "registration",
    "EAN 1": "ean1",
    "EAN 2": "ean2",
    "PRODUTO": "product",
    "APRESENTAÇÃO": "presentation",
    "CLASSE TERAPÊUTICA": "therapeutic_class",
    "TIPO DE PRODUTO (STATUS DO PRODUTO)": "product_type",
    "REGIME DE PREÇO": "price_regime",
    "TARJA": "stripe"
}

def find_header_row(file_path, keyword="CNPJ", search_limit=100):
    try:
        df_temp = pd.read_excel(file_path, engine='openpyxl', nrows=search_limit, header=None)
        
        for index, row in df_temp.iterrows():
            row_text = row.astype(str).str.cat(sep=' ').upper()
            
            if keyword.upper() in row_text:
                logger.info(f"Header found at row index: {index} (Keyword: {keyword})")
                return index
        
        logger.warning(f"Keyword '{keyword}' not found in the first {search_limit} rows. Defaulting to index 0.")
        return 0
        
    except Exception as e:
        logger.error(f"Error searching for header row: {e}", exc_info=True)
        return 0
        
def transform_data(file_path):
    logger.info("Starting data transformation process...")

    header_row_index = find_header_row(file_path, keyword="CNPJ")
    
    try:
        df_raw = pd.read_excel(
            file_path,
            engine='openpyxl',
            skiprows=header_row_index
        )
        
        logger.info(f"Raw data loaded. Shape: {df_raw.shape}")
        
        df_raw.columns = df_raw.columns.astype(str).str.strip().str.upper()

        target_cols_br = list(COLUMNS_MAP.keys())
        available_columns = [col for col in target_cols_br if col in df_raw.columns]
        
        missing_columns = set(target_cols_br) - set(available_columns)
        if missing_columns:
            logger.warning(f"Columns not found in file: {missing_columns}")

        df_filtered = df_raw[available_columns].copy()
        df_validated = df_filtered.rename(columns=COLUMNS_MAP)
        df_validated = df_validated.map(lambda x: x.strip() if isinstance(x, str) else x)

        if 'cnpj' in df_validated.columns:
            df_validated['cnpj'] = df_validated['cnpj'].astype(str).str.replace(r'\D', '', regex=True)
        
        logger.info(f"Transformation complete. Final shape: {df_validated.shape}")

        return df_raw, df_validated
    
    except Exception as e:
        logger.error(f"Error during transformation: {e}", exc_info=True)
        return None, None