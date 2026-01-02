import uuid
from datetime import datetime
from typing import Optional, Literal

from fastapi.params import Query
from pydantic import BaseModel, EmailStr

from app.schemas.abstractions.paginated_input import PaginatedInput


class UserInput(BaseModel):
    email: EmailStr
    password: str
    name: str
    last_name: str

    class Config:
        from_attributes = True


class UserUpdateInput(BaseModel):
    name: str
    last_name: str

    class Config:
        from_attributes = True


class UserOutput(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    last_name: str
    date_created: datetime
    date_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreated(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    last_name: str
    date_created: datetime
    date_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserPaginatedInput(PaginatedInput):
    email: Optional[EmailStr] = Query(None, description="Filter by email")
    name: Optional[str] = Query(None, description="Filter by name")
    last_name: Optional[str] = Query(None, description="Filter by last name")
    date_created: Optional[datetime] = Query(None, description="Filter by date_created")

    offset_field: Literal["id", "email", "date_created", "name", "last_name"] = Query(
        "id",
        description="Offset Field of the page (Ordering by Field)",
    )

    def get_offset_field(self) -> str:
        return self.offset_field
