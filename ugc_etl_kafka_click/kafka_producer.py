from kafka import KafkaProducer
import orjson
import datetime
import uuid


producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

user_id = uuid.uuid4()
film_id = uuid.uuid4()

producer.send(
    topic='views',
    value=orjson.dumps({
        'user_id': user_id,
        'film_id': film_id,
        'start_time': 11,
        'end_time': 12,
        'timestamp': datetime.datetime.now()
    }),
    key=f"{uuid.uuid4()}+{uuid.uuid4()}".encode(),
)

producer.flush()
