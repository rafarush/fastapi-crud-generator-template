from typing import Generic, TypeVar, Optional, List, Any, Callable, Sequence, Tuple
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, Row, RowMapping
from sqlmodel import SQLModel, select
from typing import Protocol

T = TypeVar("T", bound=SQLModel)


class IncludesQuery(Protocol):
    def __call__(self, query) -> Any: ...


class BaseRepository(Generic[T], ABC):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _apply_includes(query: Any, include: Optional[Callable[[Any], Any]] = None) -> Any:
        if include:
            return include(query)
        return query

    async def get_by_id(self, id: Any, include: Optional[Callable[[Any], Any]] = None) -> Optional[T]:
        base_condition = self.model.is_deleted.is_(False)
        statement = select(self.model).where(and_(base_condition, self.model.id == id))
        statement = self._apply_includes(statement, include)
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(self, include: Optional[Callable[[Any], Any]] = None, disable_tracking: bool = True) -> Sequence[
        Row[Any] | RowMapping | Any]:
        base_condition = self.model.is_deleted.is_(False)
        statement = select(self.model).where(base_condition)
        if disable_tracking:
            statement = statement.execution_options(populate_existing=False)
        statement = self._apply_includes(statement, include)
        result = self.db.execute(statement)
        return result.scalars().all()

    async def find(self, predicate: Callable[[T], Any], include: Optional[Callable[[Any], Any]] = None,
                   disable_tracking: bool = True) -> Sequence[Row[Any] | RowMapping | Any]:
        base_condition = self.model.is_deleted.is_(False)
        statement = select(self.model).where(and_(base_condition, predicate(self.model)))
        if disable_tracking:
            statement = statement.execution_options(populate_existing=False)
        statement = self._apply_includes(statement, include)
        result = self.db.execute(statement)
        return result.scalars().all()

    async def first_or_default(self, predicate: Callable[[T], Any],
                               include: Optional[Callable[[Any], Any]] = None,
                               disable_tracking: bool = True) -> Optional[T]:
        base_condition = self.model.is_deleted.is_(False)
        statement = select(self.model).where(and_(base_condition, predicate(self.model)))
        if disable_tracking:
            statement = statement.execution_options(populate_existing=False)
        statement = self._apply_includes(statement, include)
        statement = statement.limit(1)
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    async def single_or_default(self, predicate: Callable[[T], Any],
                                include: Optional[Callable[[Any], Any]] = None,
                                disable_tracking: bool = True) -> Optional[T]:
        base_condition = self.model.is_deleted.is_(False)
        statement = select(self.model).where(and_(base_condition, predicate(self.model)))
        if disable_tracking:
            statement = statement.execution_options(populate_existing=False)
        statement = self._apply_includes(statement, include)
        result = self.db.execute(statement)
        return result.scalar_one_or_none()

    async def count(self, predicate: Optional[Callable[[T], Any]] = None) -> int:
        base_condition = self.model.is_deleted.is_(False)
        statement = select(func.count()).select_from(self.model).where(base_condition)
        if predicate:
            statement = statement.where(predicate(self.model))
        result = self.db.execute(statement)
        return result.scalar() or 0

    async def any(self, predicate: Callable[[T], Any]) -> bool:
        base_condition = self.model.is_deleted.is_(False)
        statement = select(self.model).where(and_(base_condition, predicate(self.model))).limit(1)
        result = self.db.execute(statement)
        return result.first() is not None

    async def add(self, entity: T) -> Tuple[Optional[T], Optional[str]]:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity, None
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            return None, error_msg

    async def add_range(self, entities: List[T]) -> tuple[list[T], None] | tuple[None, str]:
        try:
            self.db.add_all(entities)
            self.db.commit()
            for entity in entities:
                self.db.refresh(entity)
            return entities, None
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            return None, error_msg

    async def update(self, entity: T) -> Tuple[Optional[T], Optional[str]]:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity, None
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            return None, error_msg

    async def update_range(self, entities: List[T]) -> Tuple[Optional[List[T]] , Optional[str]]:
        try:
            self.db.add_all(entities)
            self.db.commit()
            for entity in entities:
                self.db.refresh(entity)
            return entities, None
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            return None, error_msg

    async def remove(self, entity: T) -> Tuple[bool, Optional[str]]:
        try:
            self.db.delete(entity)
            self.db.commit()
            return True, None
        except IntegrityError as e:
            return False, str(e.orig)

    async def remove_range(self, entities: List[T]) -> Tuple[bool, Optional[str]]:
        try:
            for entity in entities:
                self.db.delete(entity)
            self.db.commit()
            return True, None
        except IntegrityError as e:
            return False, str(e.orig)

    async def get_paged(self, page_number: int = 1, page_size: int = 10,
                        predicate: Optional[Callable[[T], Any]] = None,
                        include: Optional[Callable[[Any], Any]] = None,
                        order_by: Optional[Callable[[T], Any]] = None,
                        ascending: bool = True,
                        disable_tracking: bool = True) -> tuple[Sequence[Row[Any] | RowMapping | Any], int | None | Any]:
        offset = (page_number - 1) * page_size
        base_condition = self.model.is_deleted.is_(False)

        # Count total
        count_stmt = select(func.count()).select_from(self.model).where(base_condition)
        if predicate:
            count_stmt = count_stmt.where(predicate(self.model))
        total_count = self.db.execute(count_stmt)
        total_count = total_count.scalar() or 0

        # Paged query
        statement = select(self.model).offset(offset).limit(page_size)
        if predicate:
            statement = statement.where(and_(base_condition, predicate(self.model)))
        else:
            statement = statement.where(base_condition)

        if disable_tracking:
            statement = statement.execution_options(populate_existing=False)
        statement = self._apply_includes(statement, include)

        if order_by:
            if ascending:
                statement = statement.order_by(asc(order_by(self.model)))
            else:
                statement = statement.order_by(desc(order_by(self.model)))

        print(statement)

        result = self.db.execute(statement)
        items = result.scalars().all()

        return items, total_count

    @property
    @abstractmethod
    def model(self) -> type[T]:
        """Must be implemented in inheritors"""
        pass
