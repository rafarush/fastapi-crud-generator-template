from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, Generic, TypeVar, List, Optional, Callable, Tuple, Sequence

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlmodel import SQLModel

from app.repositories.abstractions.base_repository import BaseRepository

T = TypeVar("T", bound=SQLModel)
TInput = TypeVar("TInput")
TUpdate = TypeVar("TUpdate")
TOutput = TypeVar("TOutput")
TPaginatedInput = TypeVar("TPaginatedInput")


class BaseService(Generic[T, TInput, TUpdate, TOutput, TPaginatedInput], ABC):
    def __init__(self, db: Session):
        self.db = db
        self.repo = self.repository_class(db)

    @property
    @abstractmethod
    def repository_class(self) -> type[BaseRepository[T]]:
        """Return concrete class of Repository (ex: UserRepository)."""
        pass

    @property
    @abstractmethod
    def model(self) -> type[T]:
        """Return related SQLModel model (ex: User)."""
        pass

    @property
    @abstractmethod
    def output_schema(self) -> type[TOutput]:
        """Return output model -output schema- (ex: UserOutput)."""
        pass

    @property
    @abstractmethod
    def created_schema(self) -> Optional[type[Any]]:
        """Return created output model -output schema- (ex: UserCreated)."""
        return None

    async def get_by_id(self, entity_id: Any):
        entity = await self.repo.get_by_id(entity_id)
        if not entity:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"{self.model.__name__} not found")

        return self.output_schema.model_validate(entity, from_attributes=True, extra="ignore")

    async def get_paged(
        self,
        params: TPaginatedInput,
        predicate_fn: Optional[Callable[[Any], Any]] = None,
        order_by_fn: Optional[Callable[[Any], Any]] = None,
    ) -> Tuple[List[TOutput], int]:
        """ Return paginated output with personalized query params """
        predicate = predicate_fn or (lambda m: True)
        entities, total = await self.repo.get_paged(
            page_number=params.page,
            page_size=params.size,
            predicate=predicate,
            order_by=order_by_fn,
            ascending=params.ascending if hasattr(params, "ascending") else True,
        )

        outputs = [
            self.output_schema.model_validate(e, from_attributes=True, extra="ignore")
            for e in entities
        ]
        return outputs, total

    async def create(self, entity_input: TInput, conflict_predicate: Optional[Callable[[T], Any]] = None):
        if conflict_predicate:
            existing = await self.repo.first_or_default(conflict_predicate)
            if existing:
                raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"{self.model.__name__} already exists")

        entity = self.model(**entity_input.dict())
        result, error = await self.repo.add(entity)

        if error:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=error)

        if self.created_schema:
            return self.created_schema.model_validate(result, from_attributes=True, extra="ignore")
        return self.output_schema.model_validate(result, from_attributes=True, extra="ignore")

    async def update(
        self,
        entity_id: Any,
        update_data: TUpdate,
        update_fn: Callable[[T, TUpdate], None]
    ):
        """Update enity using personalized mapping"""
        entity = await self.repo.first_or_default(lambda m: m.id == entity_id)
        if not entity:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"{self.model.__name__} not found")

        update_fn(entity, update_data)
        result, error = await self.repo.update(entity)

        if error:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=error)

        return self.output_schema.model_validate(result, from_attributes=True, extra="ignore")

    async def delete(self, entity_id: Any):
        entity = await self.repo.first_or_default(lambda m: m.id == entity_id)
        if not entity:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"{self.model.__name__} not found")

        success, error = await self.repo.remove(entity)
        if not success:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=error)
        return True
