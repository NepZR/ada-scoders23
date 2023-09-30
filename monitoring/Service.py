import os
from datetime import datetime
from time import sleep

from loguru import logger
from tqdm import tqdm

from acquisition.News import NewsCrawler
from controller.Database import NewsDBController


class NewsMonitoringService:
    def __init__(self) -> None:
        self.crawler = NewsCrawler()
        self.news_db = NewsDBController(collection="news")
        self.monit_db = NewsDBController(collection="monitoring")
        self.terms = [
            "genomics", "dna", "genetic diseases"
        ]

    def run(self) -> None:
        last_monit_dt = self.monit_db.retrieve_last_monitoring_dt(service="monitoring")
        time_since_last_monit = (datetime.utcnow() - last_monit_dt).seconds
        if time_since_last_monit < 3600:
            logger.info(
                f"Monitoring Service | Run >> Less than ~1 hour since the last monitoring at {last_monit_dt}. "
                f"Waiting..."
            )
            wait_progress = tqdm(range(abs(3600 - time_since_last_monit)), file=open(os.devnull, 'w'))
            for _ in wait_progress:
                sleep(1)
                if wait_progress.n % 60 == 0:
                    logger.info(str(wait_progress))

            return None

        articles_added = 0
        for article in self.crawler.get_news(search_terms=self.terms, since_hours=1):
            if self.news_db.is_document_already_inserted(data=article):
                logger.warning(
                    f"Monitoring Service | Run >> Article already present into database. Ignoring."
                )
                continue

            success = self.news_db.insert_data(data=article)
            source_name, title = article["source"]["name"], article["title"]
            if success:
                logger.success(
                    f"Monitoring Service | Run >> Article from {source_name} added successfully! Title: {title}."
                )
                articles_added += 1
            else:
                logger.error(
                    f"Monitoring Service | Run >> Article from {source_name} not indexed. "
                    f"Attempt made at {datetime.now()}. Error described above. Ignoring."
                )
                continue

        self.monit_db.insert_data(data={"terms": self.terms, "total_added": articles_added, "service": "monitoring"})
        logger.success(
            f"Monitoring Service | Run >> Monitoring finished and registered at {datetime.utcnow()}. "
            f"Next verification in ~1 hour."
        )


if __name__ == "__main__":
    monitoring = NewsMonitoringService()
    while True:
        monitoring.run()
