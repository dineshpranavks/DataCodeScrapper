from typing import List, Dict, Any
from config import ATCODER_BASE_URL
from scraper.fetch import fetch_html
from scraper.parser import parse_problems_page
from scraper.utils import setup_logger

logger = setup_logger(__name__)

def scrape_problems_for_contest(contest_id: str) -> List[Dict[str, Any]]:
    """
    Scrapes the problems for a specific contest ID.
    """
    url = f"{ATCODER_BASE_URL}/contests/{contest_id}/tasks"
    logger.info(f"Scraping problems for contest: {contest_id}")
    
    html = fetch_html(url)
    if html:
        problems = parse_problems_page(html, contest_id)
        logger.info(f"Found {len(problems)} problems for contest {contest_id}")
        return problems
        
    return []
