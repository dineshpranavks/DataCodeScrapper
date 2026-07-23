import time
import schedule
import logging
import threading
import uvicorn
from typing import List, Dict, Any

from config import UPDATE_INTERVAL_HOURS, API_PORT
from scraper.utils import setup_logger
from scraper.contest_scraper import scrape_recent_contests
from scraper.problem_scraper import scrape_problems_for_contest
from scraper.xml_export import export_contests_to_xml, export_problems_to_xml
from database.mongodb import db

logger = setup_logger(__name__)

def run_scraper_job():
    """
    Main orchestrator job that scrapes contests and problems,
    updates MongoDB, and generates XML files.
    """
    logger.info("Starting scraper job...")
    try:
        # Scrape contests (we limit to 2 pages of archives for this example, but can be configured)
        contests = scrape_recent_contests(pages=2)
        if contests:
            db.upsert_contests(contests)
            export_contests_to_xml(contests)
            
            # For each scraped contest, fetch its problems
            # Note: To avoid overloading AtCoder, we might want to only scrape problems
            # for new contests or limit the number of contests we process at once.
            all_problems = []
            for i, contest in enumerate(contests):
                # Limiting problem scraping to the first 10 recent contests to prevent long initial runtimes
                if i >= 10:
                    break
                    
                contest_id = contest.get("contest_id")
                if contest_id:
                    problems = scrape_problems_for_contest(contest_id)
                    all_problems.extend(problems)
                    # Respectful delay between contest pages is handled in fetch.py
            
            if all_problems:
                db.upsert_problems(all_problems)
                export_problems_to_xml(all_problems)
                
        logger.info("Scraper job completed successfully.")
    except Exception as e:
        logger.error(f"Error during scraper job: {e}")

def run_scheduler():
    """Runs the schedule loop."""
    logger.info(f"Scheduling scraper job every {UPDATE_INTERVAL_HOURS} hours.")
    schedule.every(UPDATE_INTERVAL_HOURS).hours.do(run_scraper_job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_api():
    """Starts the FastAPI server via Uvicorn."""
    logger.info(f"Starting API server on port {API_PORT}...")
    uvicorn.run("api:app", host="0.0.0.0", port=API_PORT, log_level="info")

if __name__ == "__main__":
    logger.info("Starting AtCoder Data Collector...")
    
    # Run the initial scraper job immediately on startup
    run_scraper_job()
    
    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start the FastAPI server in the main thread
    start_api()
