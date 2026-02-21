import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

# --- CAMINHOS ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT") 
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

if not DATABASE_URL:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- URLS E ARQUIVOS ---
ANVISA_PARENT_PAGE_URL = "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos"
ANVISA_FILE_PATTERN = r"xls_conformidade_site_.*"
LAST_DOWNLOADED_FILE = os.path.join(DATA_DIR, "last_downloaded_url.txt")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_anvisa_data.xlsx")

# --- TABELAS ---
TABLE_NAME_STAGING = "staging_anvisa_medications"
TABLE_DIM_LAB = "dim_laboratory"
TABLE_DIM_PRODUCT = "dim_product"
TABLE_FACT_MEDICATION = "fact_medication_presentation"
TABLE_NAME_ORIGINAL = "original_anvisa_medications"
TABLE_NAME_VALIDATED = "validated_anvisa_medications" 
DB_SCHEMA = "public"
AIRFLOW_CONN_ID = "postgres_default"