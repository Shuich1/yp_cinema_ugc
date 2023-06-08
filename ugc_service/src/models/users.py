from uuid import UUID

from models.base import BaseModel


class User(BaseModel):
    id: UUID
