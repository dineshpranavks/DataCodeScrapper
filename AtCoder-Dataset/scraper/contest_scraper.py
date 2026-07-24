from utils.http_client import HTTPClient
from config import ARCHIVE_URL


class ContestScraper:

    def __init__(self):

        self.client = HTTPClient()

    def scrape(self):

        html = self.client.get(ARCHIVE_URL)

        return html