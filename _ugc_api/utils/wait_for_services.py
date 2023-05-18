import os
import time

from kafka.admin import KafkaAdminClient
from kafka.errors import NoBrokersAvailable


def wait_for_kafka():
    host = os.getenv('KAFKA_HOST')
    port = os.getenv('KAFKA_PORT')

    for _ in range(60):
        try:
            admin = KafkaAdminClient(bootstrap_servers=f'{host}:{port}')
            cluster = admin.describe_cluster()
            assert 'brokers' in cluster and len(cluster.get('brokers')) > 0
            exit(0)
        except (NoBrokersAvailable, AssertionError):
            time.sleep(1)
    raise SystemExit('Unable to connect to Kafka broker.')


if __name__ == '__main__':
    wait_for_kafka()
