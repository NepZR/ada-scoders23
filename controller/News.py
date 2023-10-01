from typing import List

from acquisition.News import NewsCrawler


class NewsController:
    def __init__(self) -> None:
        self.crawler = NewsCrawler()

    def retrieve_news(self, keywords: List[str], since_hours: int = 1, language: str = "en") -> List[dict] | None:
        article_list = set()
        accepted_languages = ("en", "br")
        if language not in accepted_languages:
            raise ValueError

        for article in self.crawler.get_news(search_terms=keywords, since_hours=since_hours):
            article_list.add(article)

        if len(article_list) > 0:
            return list(article_list)

        return None
