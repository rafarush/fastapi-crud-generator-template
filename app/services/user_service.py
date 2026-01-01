import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Optional, Callable

from fastapi import HTTPException
from sqlalchemy import and_

from app.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user.user_schemas import UserInput, UserCreated, UserOutput, UserPaginatedInput, UserUpdateInput


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    async def get_user_by_id(self, user_id: uuid.UUID):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
        return UserOutput.model_validate(user, from_attributes=True, extra='ignore')

    async def get_users_paged(self, params: UserPaginatedInput):

        def predicate(model):
            conditions = []
            if params.email:
                conditions.append(model.email.ilike(f"%{params.email}%"))
            if params.name:
                conditions.append(model.name.ilike(f"%{params.name}%"))
            if params.last_name:
                conditions.append(model.last_name.ilike(f"%{params.last_name}%"))
            if params.date_created:
                conditions.append(model.email.ilike(f"%{params.id}%"))
            return and_(*conditions) if conditions else True

        def order_by(model):
            if params.get_offset_field() == "id":
                return model.id
            if params.get_offset_field() == "email":
                return model.email
            if params.get_offset_field() == "name":
                return model.name
            if params.get_offset_field() == "last_name":
                return model.last_name
            if params.get_offset_field() == "date_created":
                return model.date_created
            return model.date_created

        users, total = await self.repo.get_paged(page_number=params.page,
                                                 page_size=params.size,
                                                 predicate=predicate,
                                                 order_by=order_by,
                                                 ascending=params.ascending if params.ascending else True
                                                 )
        return [
            UserOutput.model_validate(u, from_attributes=True, extra='ignore')
            for u in users
        ], total

    async def create_user(self, user_input: UserInput):
        existing = await self.repo.first_or_default(lambda u: u.email == user_input.email)
        if existing:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Email exists")

        user = User(**user_input.dict())
        result, error = await self.repo.add(user)

        if error:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=error)

        return UserCreated(
            id=str(user.id),
            email=user.email,
            name=user.name,
            last_name=user.last_name,
            date_created=user.date_created,
            date_updated=user.date_updated,
            self=f"users/{user.id}",
        )

    async def update_user(self, user_id: uuid.UUID, user_input: UserUpdateInput):
        user = await self.repo.first_or_default(lambda u: u.id == user_id)
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

        user.name = user_input.name
        user.last_name = user.last_name
        user.date_updated = datetime.now(timezone.utc)

        result, error = await self.repo.update(user)

        if error:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=error)

        return UserOutput.model_validate(result, from_attributes=True, extra='ignore')
