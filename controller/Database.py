import os
import traceback
from datetime import datetime
from typing import Iterable

import pymongo
import pymongo.database
import pymongo.errors
from dotenv import load_dotenv
from loguru import logger


class NewsDBController:
    def __init__(self, collection: str = "news") -> None:
        load_dotenv()

        self.valid_collections = ("news", "production", "monitoring")
        if collection.lower().strip() not in self.valid_collections:
            raise ValueError(
                f"Collection name is invalid! Expected values: {self.valid_collections}. Informed value: {collection}"
            )

        self.client: pymongo.MongoClient | None = None
        self.db: pymongo.database.Database | None = None

        self.set_connection()
        self.active_collection = collection.lower().strip()
        self.collection = self.db.get_collection(collection.lower().strip())

    def set_connection(self) -> None:
        host = os.environ.get("MONGO_HOST", "localhost")
        port = int(os.environ.get("MONGO_PORT", 5433))
        usr = os.environ.get("MONGO_USR")
        pwd = os.environ.get("MONGO_PWD")

        self.client = pymongo.MongoClient(host=host, port=port, username=usr, password=pwd)
        self.db = self.client.get_database(name="scoders")

    def insert_data(self, data: dict) -> bool:
        data["entry_dt"] = datetime.utcnow()

        try:
            inserted_data = self.collection.insert_one(data)
            logger.success(
                f"Document ID {inserted_data.inserted_id} indexed into <<{self.active_collection.upper()}>> "
                f"Database at {datetime.utcnow()}. "
            )
            return True
        except Exception as e:
            logger.error(f"An error happened while attempting to index the given data into database. Exception below.")
            logger.debug(f"{traceback.print_exception(e)}")
            return False

    def read_data(self) -> Iterable:
        yield from self.collection.find()

    def retrieve_last_monitoring_dt(self, service: str) -> datetime:
        last_monitoring = self.collection.find_one({"service": service}, sort=[('entry_dt', pymongo.DESCENDING)])
        if last_monitoring is None:
            return datetime(year=2000, month=12, day=31)

        last_monitoring = last_monitoring["entry_dt"]
        return last_monitoring

    def is_document_already_inserted(self, data: dict) -> bool:
        check_params = {
            "source": data["source"]["name"],
            "title": data["title"],
            "publishedAt": data["publishedAt"],
            "search_term": data["search_term"],
        }

        documents = self.collection.find_one(check_params)
        if documents is None:
            return False

        return True
