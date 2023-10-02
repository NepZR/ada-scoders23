import os
from datetime import datetime
from time import sleep

from loguru import logger
from tqdm import tqdm

from controller.Database import NewsDBController


class NewsDataTransformerService:
    def __init__(self) -> None:
        self.daily_hour = 8
        self.news_db = NewsDBController(collection="news")
        self.prod_db = NewsDBController(collection="production")
        self.monit_db = NewsDBController(collection="monitoring")

    def _transform_data(self) -> dict:
        insights_dict = {
            "news_count_period": {
                "year": {},
                "month": {},
                "date": {},
            },
            "news_count_source": {},
            "keyword_count_period": {}
        }
        for data in self.news_db.read_data():
            keyword = data["search_term"]
            if keyword not in insights_dict["keyword_count_period"].keys():
                insights_dict["keyword_count_period"][keyword] = {
                    "year": {},
                    "month": {},
                    "date": {},
                }

            pub_dt = datetime.strptime(data["publishedAt"].split("T")[0], "%Y-%m-%d")
            pub_year, pub_month_year, pub_date = str(pub_dt.year), pub_dt.strftime("%Y-%m"), pub_dt.strftime("%Y-%m-%d")
            if pub_year not in insights_dict["news_count_period"]["year"].keys():
                insights_dict["news_count_period"]["year"][pub_year] = 0
            if pub_year not in insights_dict["keyword_count_period"][keyword]["year"].keys():
                insights_dict["keyword_count_period"][keyword]["year"][pub_year] = 0

            if pub_month_year not in insights_dict["news_count_period"]["month"].keys():
                insights_dict["news_count_period"]["month"][pub_month_year] = 0
            if pub_month_year not in insights_dict["keyword_count_period"][keyword]["month"].keys():
                insights_dict["keyword_count_period"][keyword]["month"][pub_month_year] = 0

            if pub_date not in insights_dict["news_count_period"]["date"].keys():
                insights_dict["news_count_period"]["date"][pub_date] = 0
            if pub_date not in insights_dict["keyword_count_period"][keyword]["date"].keys():
                insights_dict["keyword_count_period"][keyword]["date"][pub_date] = 0

            insights_dict["news_count_period"]["year"][pub_year] += 1
            insights_dict["news_count_period"]["month"][pub_month_year] += 1
            insights_dict["news_count_period"]["date"][pub_date] += 1
            insights_dict["keyword_count_period"][keyword]["year"][pub_year] += 1
            insights_dict["keyword_count_period"][keyword]["month"][pub_month_year] += 1
            insights_dict["keyword_count_period"][keyword]["date"][pub_date] += 1

            source, author = data["source"]["name"], data["author"]
            if source is None:
                source = "Unknown"
            if author is None:
                author = "Unknown"

            if source not in insights_dict["news_count_source"].keys():
                insights_dict["news_count_source"][source] = {}
            if author not in insights_dict["news_count_source"][source].keys():
                insights_dict["news_count_source"][source][author] = 0

            insights_dict["news_count_source"][source][author] += 1

        return insights_dict

    def run(self) -> None:
        last_monit_dt = self.monit_db.retrieve_last_monitoring_dt(service="transformer")
        last_transform_time = (datetime.utcnow() - last_monit_dt).days
        if last_transform_time < 1:
            logger.warning(
                f"Transformer Service | Run >> Less than ~24 hour since the last monitoring at {last_monit_dt}. "
                f"Waiting..."
            )
            wait_progress = tqdm(range(abs(86400 - last_transform_time)), file=open(os.devnull, 'w'))
            for _ in wait_progress:
                sleep(1)
                if wait_progress.n % 60 == 0:
                    logger.info(str(wait_progress))
            return None

        transformed_data = self._transform_data()
        self.prod_db.insert_data(data=transformed_data)

        self.monit_db.insert_data(data={"terms": None, "total_added": None, "service": "transformer"})
        logger.success(
            f"Transformer Service | Run >> Execution finished and data indexed at {datetime.utcnow()}. "
            f"Next run in ~24 hours."
        )


if __name__ == "__main__":
    t_monitoring = NewsDataTransformerService()
    while True:
        t_monitoring.run()
