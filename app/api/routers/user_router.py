# import uuid
# from typing import Annotated
#
# from fastapi import APIRouter, Depends, status
# from fastapi.params import Query
# from sqlalchemy.orm import Session
# from app.database.session import get_db
# from app.schemas.abstractions.paginated_input import PaginatedInput
# from app.schemas.abstractions.paginated_output import PaginatedOutput
# from app.schemas.user.user_schemas import UserOutput, UserInput, UserCreated, UserPaginatedInput, UserUpdateInput
# from app.services.user_service import UserService
#
# router = APIRouter()
#
#
# @router.get("/{user_id}", response_model=UserOutput)
# async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
#     service = UserService(db)
#     user = await service.get_user_by_id(user_id)
#     return user
#
#
# @router.post("/", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
# async def create_user(user_input: UserInput, db: Session = Depends(get_db)):
#     service = UserService(db)
#     return await service.create_user(user_input)
#
#
# @router.get("/", response_model=PaginatedOutput[UserOutput])
# async def get_users(db: Session = Depends(get_db),
#                     params: UserPaginatedInput = Depends()
#                     ):
#     service = UserService(db)
#     users, total = await service.get_users_paged(params)
#     return PaginatedOutput(items=users, total=total)
#
#
# @router.put("/{user_id}", response_model=UserOutput)
# async def update_user(user_input: UserUpdateInput,
#                       user_id: uuid.UUID,
#                       db: Session = Depends(get_db)):
#     service = UserService(db)
#     user = await service.update_user(user_id, user_input)
#     return user


# app/api/v1/users.py
import uuid
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.api.routers.abstractions.base_router import BaseRouter
from app.services.user_service import UserService
from app.schemas.user.user_schemas import (
    UserInput, UserUpdateInput, UserOutput, UserPaginatedInput,
)
from app.database.session import get_db
from app.services.user_service_ok import UserServiceOK


def user_service_factory(db: Session) -> UserServiceOK:
    return UserServiceOK(db)


user_base_router = BaseRouter[
    UserServiceOK,
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

# Si quieres endpoints extra específicos, puedes agregarlos aquí sobre `router`:
# @router.get("/me")
# async def get_me(...):
#     ...

