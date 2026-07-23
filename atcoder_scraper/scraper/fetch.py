import requests
import time
from typing import Optional
from scraper.utils import setup_logger

logger = setup_logger(__name__)

def fetch_html(url: str, retries: int = 3, delay: int = 2) -> Optional[str]:
    """
    Fetches the HTML content of a given URL.
    Implements retry logic and respects delay between requests to avoid overloading the server.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Fetching URL: {url} (Attempt {attempt}/{retries})")
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check if request was successful
            if response.status_code == 200:
                time.sleep(delay) # Respect delay after a successful request
                return response.text
            elif response.status_code == 404:
                logger.warning(f"URL not found (404): {url}")
                return None
            else:
                logger.warning(f"Failed to fetch {url}. Status code: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request exception for {url}: {e}")
            
        if attempt < retries:
            sleep_time = delay * (2 ** (attempt - 1)) # Exponential backoff
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

    logger.error(f"Failed to fetch {url} after {retries} attempts.")
    return None
