from typing import Optional

from app.models.user import User
from app.repositories.abstractions.base_repository import BaseRepository
from sqlalchemy.orm import Session


class UserRepository(BaseRepository[User]):
    @property
    def model(self) -> type[User]:
        return User

    # Custom functions
    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.first_or_default(lambda u: u.email == email)
