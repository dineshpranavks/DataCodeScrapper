from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import ATCODER_BASE_URL
from scraper.utils import clean_text, setup_logger

logger = setup_logger(__name__)

def parse_contests_page(html_content: str) -> List[Dict[str, Any]]:
    """
    Parses the contests page HTML and extracts a list of contests.
    """
    contests = []
    if not html_content:
        return contests
        
    soup = BeautifulSoup(html_content, 'lxml')
    # AtCoder contest tables usually sit in #contest-table-upcoming or #contest-table-recent
    # Let's target table bodies directly in typical contest listings
    tables = soup.select('.table-responsive table tbody')
    
    for tbody in tables:
        rows = tbody.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 4:
                continue
                
            try:
                # Typically: [Start Time, Contest Name, Duration, Rated Range]
                start_time_td = cols[0]
                contest_name_td = cols[1]
                duration_td = cols[2]
                rated_range_td = cols[3]
                
                a_tag = contest_name_td.find('a')
                if not a_tag:
                    continue
                    
                url = ATCODER_BASE_URL + a_tag.get('href', '')
                contest_id = url.rstrip('/').split('/')[-1]
                
                type_span = contest_name_td.find('span', class_='user-black')
                contest_type = type_span.text if type_span else None
                
                contest = {
                    "contest_id": contest_id,
                    "contest_name": clean_text(a_tag.text),
                    "contest_type": contest_type,
                    "start_time": clean_text(start_time_td.text),
                    "duration": clean_text(duration_td.text),
                    "rated_range": clean_text(rated_range_td.text),
                    "url": url,
                    "last_updated": datetime.utcnow()
                }
                contests.append(contest)
            except Exception as e:
                logger.warning(f"Error parsing a contest row: {e}")
                
    return contests

def parse_problems_page(html_content: str, contest_id: str) -> List[Dict[str, Any]]:
    """
    Parses the tasks (problems) page of a specific contest.
    """
    problems = []
    if not html_content:
        return problems
        
    soup = BeautifulSoup(html_content, 'lxml')
    # Problems table body
    tbody = soup.select_one('.table-responsive table tbody')
    if not tbody:
        logger.warning(f"No problems table found for contest: {contest_id}")
        return problems
        
    rows = tbody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        # Typical columns: [A/B/C/..., Task Name, Time Limit, Memory Limit]
        # Some contests might only have Task Name, we try to gracefully handle
        if len(cols) < 2:
            continue
            
        try:
            id_td = cols[0]
            name_td = cols[1]
            
            a_tag = name_td.find('a')
            if not a_tag:
                continue
                
            task_url = ATCODER_BASE_URL + a_tag.get('href', '')
            problem_id = task_url.rstrip('/').split('/')[-1]
            
            time_limit = clean_text(cols[2].text) if len(cols) > 2 else None
            memory_limit = clean_text(cols[3].text) if len(cols) > 3 else None
            
            problem = {
                "problem_id": problem_id,
                "contest_id": contest_id,
                "title": clean_text(a_tag.text),
                "difficulty": None, # Difficulty is usually computed externally on AtCoder or shown elsewhere
                "time_limit": time_limit,
                "memory_limit": memory_limit,
                "statement_url": task_url,
                "tags": [], # Extracted if individual task pages are visited
                "points": None, # Sometimes extracted from a separate column or task page
                "url": task_url,
                "scraped_at": datetime.utcnow()
            }
            problems.append(problem)
        except Exception as e:
            logger.warning(f"Error parsing a problem row in {contest_id}: {e}")

    return problems
