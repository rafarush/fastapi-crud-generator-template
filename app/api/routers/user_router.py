import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.params import Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.abstractions.paginated_input import PaginatedInput
from app.schemas.abstractions.paginated_output import PaginatedOutput
from app.schemas.user.user_schemas import UserOutput, UserInput, UserCreated, UserPaginatedInput, UserUpdateInput
from app.services.user_service import UserService

router = APIRouter()


@router.get("/{user_id}", response_model=UserOutput)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return user


@router.post("/", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
async def create_user(user_input: UserInput, db: Session = Depends(get_db)):
    service = UserService(db)
    return await service.create_user(user_input)


@router.get("/", response_model=PaginatedOutput[UserOutput])
async def get_users(db: Session = Depends(get_db),
                    params: UserPaginatedInput = Depends()
                    ):
    service = UserService(db)
    users, total = await service.get_users_paged(params)
    return PaginatedOutput(items=users, total=total)


@router.put("/{user_id}", response_model=UserOutput)
async def update_user(user_input: UserUpdateInput,
                      user_id: uuid.UUID,
                      db: Session = Depends(get_db)):
    service = UserService(db)
    user = await service.update_user(user_id, user_input)
    return user
