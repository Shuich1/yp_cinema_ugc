from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime


class KafkaData(BaseModel):
    user_id: UUID
    film_id: UUID
    start_time: int
    end_time: int
    timestamp: datetime


class KafkaBulkData(BaseModel):
    payload: List[KafkaData]
