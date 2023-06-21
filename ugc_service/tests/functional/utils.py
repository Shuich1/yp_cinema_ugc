from datetime import datetime, timedelta
from typing import Type
from uuid import UUID

import jwt
from pydantic import BaseModel
from pymongo.collection import Collection


def get_jtw_token(user_id: UUID) -> str:
    now = datetime.now().timestamp()
    payload = {
        'sub': str(user_id),
        'exp': now + timedelta(minutes=15).total_seconds(),
        'type': 'access',
    }
    return jwt.encode(payload, key='test', algorithm='HS256')


def write_to_db(collection: Collection, *objects: BaseModel) -> None:
    if len(objects) == 1:
        collection.insert_one(objects[0].dict())
    else:
        collection.insert_many([obj.dict() for obj in objects])


def extract_from_db(model: Type[BaseModel],
                    collection: Collection,
                    params: dict,
                    ) -> BaseModel | None:
    obj = collection.find_one(params)
    return obj and model.parse_obj(obj) or None
