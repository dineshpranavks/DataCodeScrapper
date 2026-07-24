import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from models import Contest, Problem
from config import BASE_URL, ARCHIVE_URL, HEADERS, REQUEST_DELAY

def _fetch(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(REQUEST_DELAY)
    return response.text

def get_archive() -> BeautifulSoup:
    print("Downloading archive...")
    html = _fetch(ARCHIVE_URL)
    return BeautifulSoup(html, "lxml")

def get_contests() -> list[Contest]:
    soup = get_archive()
    table = soup.find("table")
    contests = []
    if table:
        tbody = table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    a_tag = cols[1].find("a")
                    if a_tag:
                        name = a_tag.text.strip()
                        url = urljoin(BASE_URL, a_tag["href"])
                        contest_id = url.rstrip('/').split('/')[-1]
                        contests.append(Contest(contest_id=contest_id, name=name, url=url))
    print(f"Found {len(contests)} contests")
    return contests

def get_problem_urls(contest: Contest) -> list[str]:
    tasks_url = f"{contest.url}/tasks"
    html = _fetch(tasks_url)
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    urls = []
    if table:
        tbody = table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 1:
                    a_tag = cols[0].find("a")
                    if a_tag:
                        urls.append(urljoin(BASE_URL, a_tag["href"]))
    return urls

def scrape_problem(problem_url: str) -> Problem:
    html = _fetch(problem_url)
    soup = BeautifulSoup(html, "lxml")
    
    problem_id = problem_url.rstrip('/').split('/')[-1]
    # Contest ID can be inferred from the URL: /contests/abc420/tasks/abc420_a -> abc420
    parts = problem_url.split('/')
    contest_id = parts[parts.index("contests") + 1] if "contests" in parts else ""
    
    title_tag = soup.find("span", class_="h2") or soup.find("h2")
    title = title_tag.text.strip() if title_tag else ""
    
    statement = ""
    constraints = ""
    input_format = ""
    output_format = ""
    sample_inputs = []
    sample_outputs = []
    
    # Priority English sections
    lang_en = soup.find("span", class_="lang-en")
    lang_ja = soup.find("span", class_="lang-ja")
    target_lang = lang_en if lang_en else lang_ja
    
    if target_lang:
        parts = target_lang.find_all("div", class_="part")
        for part in parts:
            h3 = part.find("h3")
            if not h3:
                continue
            heading = h3.text.strip().lower()
            content = "\n".join(p.text for p in part.find_all(["p", "ul", "ol"]))
            
            if "problem statement" in heading or "問題文" in heading:
                statement = content
            elif "constraints" in heading or "制約" in heading:
                constraints = content
            elif "input" in heading or "入力" in heading:
                input_format = content
            elif "output" in heading or "出力" in heading:
                output_format = content
            elif "sample input" in heading or "入力例" in heading:
                pre = part.find("pre")
                if pre:
                    sample_inputs.append(pre.text.strip())
            elif "sample output" in heading or "出力例" in heading:
                pre = part.find("pre")
                if pre:
                    sample_outputs.append(pre.text.strip())
                    
    # Parse limits
    time_limit = "2 sec"
    memory_limit = "1024 MB"
    # Basic scraping for limits typically found in <p> Time Limit: ... </p>
    for p in soup.find_all("p"):
        if "Time Limit:" in p.text:
            text = p.text
            try:
                time_limit = text.split("Time Limit:")[1].split("/")[0].strip()
                memory_limit = text.split("Memory Limit:")[1].strip()
            except IndexError:
                pass
            
    return Problem(
        problem_id=problem_id,
        contest_id=contest_id,
        problem_url=problem_url,
        title=title,
        statement=statement,
        constraints=constraints,
        input_format=input_format,
        output_format=output_format,
        sample_inputs=sample_inputs,
        sample_outputs=sample_outputs,
        time_limit=time_limit,
        memory_limit=memory_limit
    )

def scrape_contest(contest: Contest) -> list[Problem]:
    print(f"Scraping {contest.name}...")
    problem_urls = get_problem_urls(contest)
    print(f"Found {len(problem_urls)} problems")
    problems = []
    for url in problem_urls:
        problem_id = url.split('/')[-1]
        print(f"Scraping {problem_id}")
        try:
            problem = scrape_problem(url)
            problems.append(problem)
            print(f"Completed {problem_id}")
        except Exception as e:
            print(f"Failed to scrape {problem_id}: {e}")
    return problems

def scrape_all_contests(limit=None) -> dict[Contest, list[Problem]]:
    contests = get_contests()
    if limit is not None:
        contests = contests[:limit]
        
    results = {}
    for contest in contests:
        results[contest] = scrape_contest(contest)
        
    return results

if __name__ == "__main__":
    contests = get_contests()
    print(f"Total contests retrieved: {len(contests)}")
    if contests:
        problems = scrape_contest(contests[0])
        if problems:
            print(f"First problem of first contest: {problems[0].title}")
