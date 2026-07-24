import time
from datetime import datetime
import sys
from pathlib import Path

# Ensure modules can be imported
sys.path.append(str(Path(__file__).resolve().parent))

from scraper import get_contests, get_problem_urls, scrape_problem
from database.database import Database
from classifier.ai_classifier import AIClassifier
from exporter.xml_exporter import XMLExporter

class Pipeline:
    """
    Main orchestrator for the AtCoder Dataset Generator.
    """

    def __init__(self, contest_limit: int = None, classify: bool = True, export_xml: bool = True, resume: bool = False):
        self.contest_limit = contest_limit
        self.run_classify = classify
        self.run_export = export_xml
        self.resume = resume
        
        self.db = None
        self.classifier = None
        self.exporter = None
        
        self.stats = {
            "contests_processed": 0,
            "problems_scraped": 0,
            "problems_skipped": 0,
            "classified": 0,
            "xml_generated": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }

    def initialize(self):
        """
        Initializes the Database, AI Classifier, and XML Exporter.
        """
        print("==================================")
        print("AtCoder Dataset Generator")
        print("==================================")
        
        try:
            self.db = Database()
            if self.run_classify:
                self.classifier = AIClassifier()
            if self.run_export:
                self.exporter = XMLExporter()
        except Exception as e:
            print(f"Initialization failed: {e}")
            self.stats["errors"] += 1
            raise

    def scrape(self):
        """
        Orchestrates scraping of contests and problems.
        """
        try:
            contests = get_contests()
        except Exception as e:
            print(f"Failed to fetch contests: {e}")
            self.stats["errors"] += 1
            return

        if self.contest_limit is not None:
            contests = contests[:self.contest_limit]
            
        print(f"Found {len(contests)} contests")
        
        for i, contest in enumerate(contests, 1):
            print(f"Processing Contest {i}/{len(contests)}")
            print(contest.name)
            
            try:
                # Insert contest gracefully skips duplicates in DB level, but resume flag dictates pipeline behavior
                if self.resume and self.db.contest_exists(contest.contest_id):
                    # We still need to process its problems if we resumed, 
                    # but if we strictly "Skip existing contests" per requirements:
                    print("Contest exists, skipping due to --resume")
                    self.stats["contests_processed"] += 1
                    continue
                
                self.db.insert_contest(contest)
                
                problem_urls = get_problem_urls(contest)
                print(f"{len(problem_urls)} Problems Found")
                
                saved_count = 0
                for url in problem_urls:
                    problem_id = url.rstrip('/').split('/')[-1]
                    
                    if self.resume and self.db.problem_exists(problem_id):
                        self.stats["problems_skipped"] += 1
                        continue
                        
                    try:
                        problem = scrape_problem(url)
                        self.db.insert_problem(problem)
                        self.stats["problems_scraped"] += 1
                        saved_count += 1
                    except Exception as e:
                        print(f"Failed to scrape problem {problem_id}: {e}")
                        self.stats["errors"] += 1
                    
                print(f"Saved {saved_count} Problems")
                self.stats["contests_processed"] += 1
                
            except Exception as e:
                print(f"Error processing contest {contest.contest_id}: {e}")
                self.stats["errors"] += 1

    def classify(self):
        """
        Orchestrates AI classification for unclassified problems.
        """
        if not self.run_classify:
            return
            
        print("Classification Started")
        try:
            all_problems = self.db.get_all_problems()
            unclassified = [p for p in all_problems if not p.topic]
            print(f"{len(unclassified)} Problems Remaining")
            
            for problem in unclassified:
                try:
                    classification = self.classifier.classify(problem)
                    if classification:
                        problem.topic = classification.topic
                        problem.subtopic = classification.subtopic
                        problem.difficulty = classification.difficulty
                        problem.rating = classification.estimated_rating
                        
                        self.db.update_problem(problem)
                        self.stats["classified"] += 1
                    else:
                        self.stats["errors"] += 1
                except Exception as e:
                    print(f"Classification failed for {problem.problem_id}: {e}")
                    self.stats["errors"] += 1
                    
            print("Classification Completed")
            
        except Exception as e:
            print(f"Classification process encountered an error: {e}")
            self.stats["errors"] += 1

    def export(self):
        """
        Orchestrates XML export for all problems in the database.
        """
        if not self.run_export:
            return
            
        print("Generating XML Files")
        try:
            problems = self.db.get_all_problems()
            # XML Exporter naturally overwrites files by writing in wb mode
            paths = self.exporter.export_all(problems)
            self.stats["xml_generated"] = len(paths)
        except Exception as e:
            print(f"XML export failed: {e}")
            self.stats["errors"] += 1

    def summary(self):
        """
        Outputs the final execution statistics.
        """
        print("====================================")
        print("Dataset Generation Complete")
        print("====================================")
        print(f"Contests Processed : {self.stats['contests_processed']}")
        print(f"Problems Scraped : {self.stats['problems_scraped']}")
        print(f"Problems Stored : {self.stats['problems_scraped']}")
        print(f"Problems Classified : {self.stats['classified']}")
        print(f"XML Files Generated : {self.stats['xml_generated']}")
        print(f"Errors : {self.stats['errors']}")
        
        if self.stats["start_time"] and self.stats["end_time"]:
            delta = self.stats["end_time"] - self.stats["start_time"]
            total_seconds = int(delta.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"Execution Time : {hours:02d}:{minutes:02d}:{seconds:02d}")
        print("====================================")

    def run(self):
        """
        Executes the entire end-to-end workflow.
        """
        self.stats["start_time"] = datetime.now()
        try:
            self.initialize()
            self.scrape()
            self.classify()
            self.export()
        except Exception as e:
            print(f"Fatal pipeline error: {e}")
            self.stats["errors"] += 1
        finally:
            self.stats["end_time"] = datetime.now()
            self.summary()
            if self.db:
                self.db.close()
