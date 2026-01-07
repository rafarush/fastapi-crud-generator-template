import uuid
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.api.routers.abstractions.base_router import BaseRouter
from app.schemas.user.user_schemas import (
    UserInput, UserUpdateInput, UserOutput, UserPaginatedInput,
)
from app.database.session import get_db
from app.services.user_service import UserService


def user_service_factory(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


user_base_router = BaseRouter[
    UserService,
    UserInput,
    UserUpdateInput,
    UserOutput,
    UserPaginatedInput
](
    service_factory=user_service_factory,
    input_schema=UserInput,
    update_schema=UserUpdateInput,
    output_schema=UserOutput,
    paginated_input_schema=UserPaginatedInput,
    prefix="/users",
    tags=["Users"],
    id_type=uuid.UUID,
)

router: APIRouter = user_base_router.router


# Add custom endpoints using router:
# @router.get("/me")
# async def get_me(...):
#     ...

@router.get("/users/by_email/{email}")
async def by_email(
    email: str,
    user_service: UserService = Depends(user_service_factory),
):
    return await user_service.get_user_by_email(email)

