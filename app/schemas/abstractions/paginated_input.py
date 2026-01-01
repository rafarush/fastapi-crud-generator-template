from fastapi.params import Query
from pydantic import BaseModel, ConfigDict


class PaginatedInput(BaseModel):
    page: int = Query(1, ge=1, description='Page number')
    size: int = Query(10, ge=1, le=100, description='Size of the page')
    ascending: bool = Query(True, description='Ascending')

    model_config = ConfigDict(extra='ignore')

    def get_offset_field(self) -> str:
        raise NotImplementedError("Subclasses must implement get_offset_field()")
