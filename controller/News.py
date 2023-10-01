from typing import List

from loguru import logger

from acquisition.News import NewsCrawler
from controller.Database import NewsDBController


class NewsController:
    def __init__(self) -> None:
        self.crawler = NewsCrawler()
        self.news_db = NewsDBController(collection="news")
        self.monit_db = NewsDBController(collection="monitoring")

    def _register_webhook_call(self, keywords: List[str], total_added: int) -> None:
        self.monit_db.insert_data(
            data={"terms": keywords, "total_added": total_added, "service": "webhook"}
        )

    def retrieve_news(self, keywords: List[str], since_hours: int = 1, language: str = "en") -> List[dict] | None:
        article_list = []
        accepted_languages = ("en", "br")
        if language not in accepted_languages:
            raise ValueError

        total_indexed = 0
        for article in self.crawler.get_news(search_terms=keywords, since_hours=since_hours):
            if self.news_db.is_document_already_inserted(data=article):
                logger.warning(
                    f"Webhook API | Search >> Article already present into database. Skipping Index."
                )
            else:
                self.news_db.insert_data(data=article)
                total_indexed += 1

            article_list.append(article)
        self._register_webhook_call(keywords=keywords, total_added=total_indexed)

        articles_fetched = len(article_list)
        if articles_fetched > 0:
            return article_list

        return None
