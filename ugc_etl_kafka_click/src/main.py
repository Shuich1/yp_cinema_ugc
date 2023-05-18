from extract.base import KafkaExtractor
from transform.base import Transformer
from load.base import ClickhouseLoader
from logging import getLogger
from time import sleep
from core.config import settings


logger = getLogger(__name__)


def main():
    transofmer = Transformer()
    with (
        KafkaExtractor(settings.KAFKA_TOPIC, settings.KAFKA_SERVER, settings.KAFKA_GROUPID) as extractor,
        ClickhouseLoader(settings.CLICKHOUSE_HOST) as loader
    ):
        for kafka_bulk_data in extractor.get_updates():
            if kafka_bulk_data.payload:
                transformed_data = transofmer.kafka_to_clickhouse(kafka_bulk_data, settings.CLICKHOUSE_TABLENAME)
                loader.load(transformed_data)
                sleep(5)


if __name__ == "__main__":
    main()
