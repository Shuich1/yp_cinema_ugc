from logging import getLogger
from extract.schema import KafkaBulkData
from load.schema import ClickhouseBulkData


logger = getLogger(__name__)


class Transformer:

    def __init__(self) -> None:
        pass

    def kafka_to_clickhouse(self, kafka_bulk_data: KafkaBulkData, click_table_name: str) -> ClickhouseBulkData:
        query_strings = [f"INSERT INTO {click_table_name} (user_id, film_id, start_time, end_time, event_time) VALUES "]
        for row in kafka_bulk_data.payload:
            timestamp = row.timestamp.replace(tzinfo=None, microsecond=0)
            query_strings.append(
                f"('{row.user_id}', '{row.film_id}', {row.start_time}, {row.end_time}, '{timestamp}'),"
            )
        result = ClickhouseBulkData(query=''.join(query_strings), count=len(query_strings) - 1)
        return result
