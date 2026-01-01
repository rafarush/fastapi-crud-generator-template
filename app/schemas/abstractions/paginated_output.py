from typing import List, Any, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar('T')


class PaginatedOutput(BaseModel, Generic[T]):
    items: List[Any]
    total: int

    class Config:
        from_attributes = True
