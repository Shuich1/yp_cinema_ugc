import logging.config
import os

from client.clickhouse import ClickHouseClient
from client.vertica import VerticaClient
from suite import TestSuite

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
        },
    },
})
logger = logging.getLogger(__name__)

info_template = '''
Running speed tests
- Initial rows:     {0}
- Stress tests WPS: {1}
- Readers count:    {2}'''


def main():
    rows_count = int(os.getenv('INITIAL_ROWS_COUNT', 100_000))
    wps = int(os.getenv('STRESS_TESTS_WPS', 10_000))
    readers_count = int(os.getenv('READERS_COUNT', 5))

    test_suite = TestSuite(
        rows_count=rows_count,
        wps=wps,
        readers_count=readers_count,
    )
    logger.info(info_template.format(rows_count, wps, readers_count))

    clickhouse_client = ClickHouseClient(
        host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
        port=int(os.getenv('CLICKHOUSE_PORT', 9000)),
    )
    test_suite.register(clickhouse_client)

    vertica_client = VerticaClient(
        host=os.getenv('VERTICA_HOST', '127.0.0.1'),
        port=int(os.getenv('VERTICA_PORT', 5433)),
        user='dbadmin',
        database='docker',
        autocommit=True,
    )
    test_suite.register(vertica_client)

    for result in test_suite.run():
        logger.info(result.log_message)


if __name__ == '__main__':
    main()
