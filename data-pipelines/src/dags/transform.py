import pandas as pd
import logging

logger = logging.getLogger(__name__)

TARGET_COLUMNS = [
    "SUBSTÂNCIA",
    "CNPJ",
    "LABORATÓRIO",
    "CÓDIGO GGREM",
    "REGISTRO",
    "EAN 1",
    "EAN 2",
    "PRODUTO",
    "APRESENTAÇÃO",
    "CLASSE TERAPÊUTICA",
    "TIPO DE PRODUTO (STATUS DO PRODUTO)",
    "REGIME DE PREÇO",
    "TARJA"
]

def find_header_row(file_path, keyword="CNPJ", search_limit=100):
    """
    Scans the first few rows of the Excel file to find the row index 
    containing the specified keyword (header row).
    """
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

def transform_data(raw_data_path):
    logger.info("Starting data transformation process...")
    
    # 1. Dynamic Header Search
    # Procura onde começam os dados reais (baseado na coluna CNPJ)
    header_row_index = find_header_row(raw_data_path, keyword="CNPJ")
    
    try:
        # 2. Load Data
        # Carrega o Excel pulando o cabeçalho inútil
        df_full = pd.read_excel(
            raw_data_path,
            engine='openpyxl',
            skiprows=header_row_index
        )
        
        logger.info(f"Raw data loaded. Shape before filtering: {df_full.shape}")
        
        # 3. Normalize Column Names
        # Remove espaços e coloca tudo em maiúsculo para bater com a lista TARGET_COLUMNS
        df_full.columns = df_full.columns.astype(str).str.strip().str.upper()

        # 4. Filter Columns
        # Seleciona apenas as colunas que existem no arquivo E estão na sua lista
        available_columns = [col for col in TARGET_COLUMNS if col in df_full.columns]
        
        # Verifica se faltou alguma coluna importante
        missing_columns = set(TARGET_COLUMNS) - set(available_columns)
        if missing_columns:
            logger.warning(f"The following target columns were not found in the file: {missing_columns}")

        # Cria o DataFrame final apenas com as colunas desejadas
        df_filtered = df_full[available_columns].copy()
        
        logger.info(f"Column filtering complete. Final shape: {df_filtered.shape}")

        # 5. Return Data
        # Como removemos a lógica de validação antiga, retornamos o df filtrado 
        # para ambas as variáveis para não quebrar o main.py
        return df_filtered, df_filtered
    
    except Exception as e:
        logger.error(f"Error during transformation: {e}", exc_info=True)
        return None, None