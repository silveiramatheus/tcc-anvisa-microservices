import requests
import os
import logging
import config
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

from airflow.models import Variable

logger = logging.getLogger(__name__)

def scrape_latest_download_url(parent_page_url, file_pattern):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        page_response = requests.get(parent_page_url, headers=headers, timeout=10)
        page_response.raise_for_status()
        
        soup = BeautifulSoup(page_response.content, 'html.parser')
        pattern = re.compile(file_pattern)
        
        link_tag = soup.find('a', href=pattern)

        if not link_tag:
            logger.error(f"Link not found with pattern: {file_pattern}")
            return None
        
        final_link = link_tag['href']
        dynamic_url = urljoin(parent_page_url, final_link)

        logger.info(f"Found download URL: {dynamic_url}")
        return dynamic_url
    
    except requests.RequestException as e:
        logger.error(f"Error during scraping the download URL: {e}", exc_info=True)
        return None
    
def get_last_downloaded_url():
    return Variable.get("anvisa_last_downloaded_url", default_var=None)

def set_last_downloaded_url(url):
    Variable.set("anvisa_last_downloaded_url", url)

def download_check():
    logger.info("Starting file download process...")

    scraped_url = scrape_latest_download_url(
        config.ANVISA_PARENT_PAGE_URL,
        config.ANVISA_FILE_PATTERN
    )

    if not scraped_url:
        logger.error("Failed to retrieve the download URL.")
        return False, None
    
    local_url = get_last_downloaded_url()

    if local_url == scraped_url:
        logger.info("No updates found. The local file is already at the latest version.")
        return False, config.RAW_DATA_PATH
    
    logger.info(f"New data available. Downloading the latest version. Old URL: {local_url}, New URL: {scraped_url}")
    return download_file(scraped_url)
    
def download_file(download_url):
    try:
        get_response = requests.get(download_url, stream=True, timeout=60)
        get_response.raise_for_status()
        os.makedirs(config.DATA_DIR, exist_ok=True)

        with open(config.RAW_DATA_PATH, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"File downloaded successfully to {config.RAW_DATA_PATH}")
        
        set_last_downloaded_url(download_url)
        logger.info(f"Updated last downloaded URL to {download_url}")
        
        return True, config.RAW_DATA_PATH
    
    except requests.RequestException as e:
        logger.error(f"Error during file download: {e}", exc_info=True)
        return False, None