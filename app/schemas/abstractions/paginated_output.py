from typing import List, Any, TypeVar, Generic

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class PaginatedOutput(BaseModel, Generic[T]):
    items: List[Any]
    total: int

    model_config = ConfigDict(from_attributes=True)
