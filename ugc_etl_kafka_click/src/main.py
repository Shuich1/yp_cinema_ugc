from extract.base import KafkaExtractor
from transform.base import Transformer
from load.base import ClickhouseLoader
from logging import getLogger
from time import sleep
from core.config import settings


logger = getLogger(__name__)


def main():
    transofmer = Transformer()
    with KafkaExtractor(
            settings.kafka_topic,
            settings.kafka_server,
            settings.kafka_groupid
        ) as extractor, \
            ClickhouseLoader(settings.clickhouse_host) as loader:

        for kafka_bulk_data in extractor.get_updates():
            if kafka_bulk_data.payload:
                transformed_data = transofmer.kafka_to_clickhouse(
                    kafka_bulk_data,
                    settings.clickhouse_tablename
                )
                loader.load(transformed_data)
            sleep(settings.sleep_interval)


if __name__ == "__main__":
    main()
