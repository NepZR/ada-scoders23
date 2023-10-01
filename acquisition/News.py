import os
import re
from datetime import datetime, timedelta
from math import ceil
from typing import Iterable, List

import requests
from dotenv import load_dotenv
from loguru import logger


class NewsCrawler:
    def __init__(self) -> None:
        load_dotenv()

        self.api_endpoint = "https://newsapi.org/v2/everything"
        self.api_key = os.environ.get("API_KEY")

    @staticmethod
    def _make_search_str(terms_list: List[str]) -> str:
        search_str = ""
        for term in terms_list:
            if len(term.split()) > 1:
                search_str += f"\"{term.strip()}\""
            else:
                search_str += term

            search_str += " OR "

        search_str = re.sub(r"( OR )$", "", search_str).strip()
        return search_str

    @staticmethod
    def _make_search_terms(terms_list: List[str]) -> List[str]:
        terms_fmt = set()
        for term in terms_list:
            if len(term.split()) > 1:
                terms_fmt.add(f"\"{term.lower().strip()}\"")
            else:
                terms_fmt.add(term.lower().strip())

        return list(terms_fmt)

    def _make_api_request(self, query_data: dict) -> dict:
        response = requests.get(url=self.api_endpoint, params=query_data)
        if response.status_code != 200:
            err_message = response.text
            raise ConnectionError(
                f"News Crawler | API >> Error getting data from NewsAPI. "
                f"Error Message: {err_message}. Halting execution."
            )

        r_data = response.json()
        return r_data

    def get_news(self, search_terms: List[str], since_hours: int = 1, language: str = "en") -> Iterable[dict]:
        search_terms_fmt = self._make_search_terms(terms_list=search_terms)
        initial_date = (datetime.now() - timedelta(hours=since_hours)).strftime("%Y-%m-%dT%H:%M:%S")
        final_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        query_params = {
            "q": "",
            "from": initial_date,
            "to": final_date,
            "language": language,
            "sortBy": "publishedAt",
            "apiKey": self.api_key
        }

        for term in search_terms_fmt:
            logger.info(
                f"News Crawler | API >> Getting data between {initial_date} and {final_date} for TERM {term}."
            )
            query_params["q"] = term

            try:
                r_data = self._make_api_request(query_data=query_params)
            except ConnectionError:
                r_data = {"totalResults": 0, "articles": []}

            total_results = r_data["totalResults"]
            total_pages = ceil(total_results / 100)

            if not total_results == 0:
                logger.debug(
                    f"News Crawler | API >> Total of {total_pages} Articles found in {total_pages} pages."
                )
            else:
                logger.warning(
                    f"News Crawler | API >> No articles were found for the specified query."
                )

            for curr_page in range(1, total_pages + 1):
                if curr_page > 1:
                    query_params["page"] = curr_page
                    r_data = self._make_api_request(query_data=query_params)

                logger.info(
                    f"News Crawler | API >> Extracting data from Page {curr_page} of {total_pages}."
                )

                page_articles = r_data["articles"]
                for article_no, article in enumerate(page_articles):
                    logger.warning(
                        f"News Crawler | Extraction [Page {curr_page}] >> "
                        f"Extracting data from Article {article_no + 1}."
                    )
                    article["search_term"] = term
                    yield article

        logger.success(
            f"News Crawler | Extraction >> Article Data Extraction completed successfully at {datetime.now()}."
        )


if __name__ == "__main__":
    crawler = NewsCrawler()
    terms = [
        "genomics", "medicine", "genomic analysis"
    ]

    for article_doc in crawler.get_news(search_terms=terms, since_hours=1):
        pass
