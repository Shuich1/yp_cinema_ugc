from pydantic import BaseModel


class ClickhouseBulkData(BaseModel):
    count: int
    query: str
