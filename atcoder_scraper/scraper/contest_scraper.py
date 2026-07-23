from typing import List, Dict, Any
from config import ATCODER_BASE_URL
from scraper.fetch import fetch_html
from scraper.parser import parse_contests_page
from scraper.utils import setup_logger

logger = setup_logger(__name__)

def scrape_recent_contests(pages: int = 2) -> List[Dict[str, Any]]:
    """
    Scrapes the most recent contests from the AtCoder archive pages.
    """
    all_contests = []
    
    # Also fetch upcoming and active contests from the main /contests page
    logger.info("Scraping upcoming and active contests")
    main_url = f"{ATCODER_BASE_URL}/contests"
    html = fetch_html(main_url)
    if html:
        all_contests.extend(parse_contests_page(html))
        
    # Fetch archived past contests
    for page in range(1, pages + 1):
        url = f"{ATCODER_BASE_URL}/contests/archive?page={page}"
        logger.info(f"Scraping past contests from archive page {page}")
        html = fetch_html(url)
        if html:
            contests = parse_contests_page(html)
            if not contests:
                break # No more contests
            all_contests.extend(contests)
            
    logger.info(f"Total contests scraped: {len(all_contests)}")
    return all_contests
