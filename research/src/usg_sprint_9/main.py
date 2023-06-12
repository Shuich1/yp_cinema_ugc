import sys
import os
import logging.config

from suite import TestSuite

# Temporarily add the parent directory to the Python path
original_path = sys.path.copy()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from client.postgres import PostgresClient
from client.mongodb import MongoDBClient

# Restore the original Python path
sys.path = original_path

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "INFO",
            },
        },
    }
)
logger = logging.getLogger(__name__)

info_template = """
Running speed tests
- Initial rows:     {0}
- Stress tests WPS: {1}
- Readers count:    {2}"""


def main():
    rows_count = int(os.getenv("INITIAL_ROWS_COUNT", 100_000))
    wps = int(os.getenv("STRESS_TESTS_WPS", 10_000))
    readers_count = int(os.getenv("READERS_COUNT", 5))

    test_suite = TestSuite(
        rows_count=rows_count,
        wps=wps,
        readers_count=readers_count,
    )
    logger.info(info_template.format(rows_count, wps, readers_count))

    postgres_client = PostgresClient(
        host="postgres", port=5432, user="app", password="123qwe", database="movie_db_usg_9_test"
    )

    test_suite.register(postgres_client)

    mongo_db_client = MongoDBClient(host="mongosingle", port=27017)

    test_suite.register(mongo_db_client)

    for result in test_suite.run():
        logger.info(result.log_message)


if __name__ == "__main__":
    main()
