# AtCoder Data Collector

A production-ready web scraping project that collects programming contest and problem data from AtCoder using BeautifulSoup, stores it in MongoDB, and exports to XML. 
Additionally, it provides a FastAPI-powered REST API to retrieve the scraped data.

## Features

- **Web Scraping:** Uses BeautifulSoup4, Requests, and lxml to efficiently extract contest and problem data.
- **Robustness:** Implements retry logic with exponential backoff and respectful delays to avoid overloading the AtCoder servers.
- **Database:** Stores data in a local MongoDB database with `upsert` logic, automatically avoiding duplicates.
- **Automated Scheduling:** Uses the `schedule` library to automatically update the database every 24 hours.
- **XML Export:** Automatically generates `contests.xml` and `problems.xml`.
- **REST API:** FastAPI application that serves the scraped data.

## Project Structure

```
atcoder_scraper/
├── main.py                 # Application entrypoint (starts scheduler and API)
├── api.py                  # FastAPI endpoints
├── config.py               # Configuration loading
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables
├── database/               # MongoDB models and connection manager
├── scraper/                # Fetching, parsing, and exporting logic
├── xml/                    # Generated XML files
└── logs/                   # Log files
```

## Setup Instructions

### Prerequisites
- Python 3.12+
- MongoDB installed and running locally on port 27017 (or configure via `.env`)

### Installation

1. Navigate to the project directory:
   ```bash
   cd atcoder_scraper
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify or modify the `.env` file for your configuration:
   ```env
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DB_NAME=atcoder
   UPDATE_INTERVAL_HOURS=24
   API_PORT=8000
   ```

### Running the Application

To run the complete system (which starts the initial scraping job, sets up the 24-hour scheduler, and launches the FastAPI server):

```bash
python main.py
```

*Note: The first run will scrape the recent contests and problems. Check `logs/scraper.log` to monitor the progress.*

### Running only the API (Dev mode)

If you only want to run the REST API and have hot-reloading enabled:

```bash
uvicorn api:app --reload --port 8000
```

## API Endpoints

Once the application is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Available Endpoints:**
- `GET /contests` - Retrieve paginated contests
- `GET /contests/{id}` - Retrieve a specific contest
- `GET /problems` - Retrieve paginated problems (optionally filter by `contest_id`)
- `GET /problems/{id}` - Retrieve a specific problem
- `GET /search?keyword=...` - Search for contests or problems by keyword
- `GET /difficulty/{level}` - Retrieve problems by difficulty
- `GET /export/xml?type=contests` - Download the exported contests XML
- `GET /export/xml?type=problems` - Download the exported problems XML
