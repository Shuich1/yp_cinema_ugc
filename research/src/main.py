from client.clickhouse import ClickHouseClient
from client.vertica import VerticaClient

from suite import TestSuite


def main():
    test_suite = TestSuite(rows_count=100_000, wps=10_000)

    clickhouse_client = ClickHouseClient(host='localhost')
    test_suite.register(clickhouse_client)

    vertica_client = VerticaClient(
        host='127.0.0.1',
        port=5433,
        user='dbadmin',
        database='docker',
        autocommit=True,
    )
    test_suite.register(vertica_client)

    for result in test_suite.run():
        print(result.log_message)


if __name__ == '__main__':
    main()
