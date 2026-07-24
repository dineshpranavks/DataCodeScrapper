import argparse
import sys
from pathlib import Path

# Ensure local imports work correctly
sys.path.append(str(Path(__file__).resolve().parent))

from pipeline import Pipeline

def main():
    parser = argparse.ArgumentParser(description="AtCoder Dataset Generator Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Only scrape first N contests")
    parser.add_argument("--no-classify", action="store_true", help="Skip AI classification")
    parser.add_argument("--no-export", action="store_true", help="Skip XML export")
    parser.add_argument("--resume", action="store_true", help="Resume from existing SQLite database")
    
    args = parser.parse_args()
    
    pipeline = Pipeline(
        contest_limit=args.limit,
        classify=not args.no_classify,
        export_xml=not args.no_export,
        resume=args.resume
    )
    
    try:
        pipeline.run()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        pipeline.stats["errors"] += 1
        pipeline.summary()
        if pipeline.db:
            pipeline.db.close()
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()