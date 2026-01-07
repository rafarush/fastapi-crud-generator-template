from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import and_
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user.user_schemas import (
    UserInput, UserCreated, UserOutput, UserUpdateInput, UserPaginatedInput
)
from app.services.abstractions.base_service import BaseService


class UserService(BaseService[User, UserInput, UserUpdateInput, UserOutput, UserPaginatedInput]):

    @property
    def repository_class(self):
        return UserRepository

    @property
    def model(self):
        return User

    @property
    def output_schema(self):
        return UserOutput

    @property
    def created_schema(self):
        return UserCreated

    async def get_users_paged(self, params: UserPaginatedInput):
        def predicate(model):
            conditions = []
            if params.email:
                conditions.append(model.email.ilike(f"%{params.email}%"))
            if params.name:
                conditions.append(model.name.ilike(f"%{params.name}%"))
            if params.last_name:
                conditions.append(model.last_name.ilike(f"%{params.last_name}%"))
            return and_(*conditions) if conditions else True

        def order_by(model):
            return getattr(model, params.get_offset_field() or "date_created")

        users, total = await self.get_paged(params, predicate_fn=predicate, order_by_fn=order_by)

        return [
            UserOutput.model_validate(u, from_attributes=True, extra='ignore')
            for u in users
        ], total

    async def create_user(self, user_input: UserInput):
        return await self.create(user_input, conflict_predicate=lambda u: u.email == user_input.email)

    async def update_item(self, user_id: uuid.UUID, user_input: UserUpdateInput):
        def updater(entity: User, data: UserUpdateInput):
            entity.name = data.name
            entity.last_name = data.last_name
            entity.date_updated = datetime.now(timezone.utc)

        return await self.update(user_id, user_input, updater)

    # Custom methods

    async def get_user_by_email(self, email: str):
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        return self.output_schema.model_validate(user, from_attributes=True, extra="ignore")
