from services.producer import Producer, KafkaProducer

producer: Producer = KafkaProducer()


async def get_producer() -> Producer:
    return producer
