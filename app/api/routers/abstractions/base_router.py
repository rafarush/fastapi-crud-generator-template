from typing import TypeVar, Generic, Callable, Type, Optional, List, Any, Tuple
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.database.session import get_db
from app.schemas.abstractions.paginated_output import PaginatedOutput
from app.services.abstractions.base_service import BaseService

TService = TypeVar("TService", bound=BaseService)
TInput = TypeVar("TInput")
TUpdate = TypeVar("TUpdate")
TOutput = TypeVar("TOutput")
TPaginatedInput = TypeVar("TPaginatedInput")


def get_service_dependency(service_factory: Callable[[Session], Any]):
    """Dependency to inject service."""

    def _dependency(db: Session = Depends(get_db)) -> Any:
        return service_factory(db)

    return _dependency


class BaseRouter(Generic[TService, TInput, TUpdate, TOutput, TPaginatedInput]):
    def __init__(
            self,
            *,
            service_factory: Callable[[Session], TService],
            input_schema: Type[TInput],
            update_schema: Type[TUpdate],
            output_schema: Type[TOutput],
            paginated_input_schema: Type[TPaginatedInput],
            prefix: str,
            tags: Optional[list[str]] = None,
            id_type: Type[Any] = str,  # uuid.UUID, int, etc.
    ):
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self.service_factory = service_factory
        self.input_schema = input_schema
        self.update_schema = update_schema
        self.output_schema = output_schema
        self.paginated_input_schema = paginated_input_schema
        self.id_type = id_type
        self.service_dependency = get_service_dependency(service_factory)
        self._register_routes()

    def _register_routes(self):

        id_type = self.id_type
        paginated_input_schema = self.paginated_input_schema
        input_schema = self.input_schema
        update_schema = self.update_schema

        # GET /{id}
        @self.router.get(
            "/{item_id}",
            response_model=self.output_schema,
            status_code=status.HTTP_200_OK,
        )
        async def get_by_id(
                item_id: id_type,
                service: TService = Depends(self.service_dependency),
        ):
            return await service.get_by_id(item_id)

        # GET /
        @self.router.get(
            "/",
            response_model=PaginatedOutput[self.output_schema],  # (items, total)
            status_code=status.HTTP_200_OK,
        )
        async def get_paged(
                params: paginated_input_schema = Depends(paginated_input_schema),
                service: TService = Depends(self.service_dependency),
        ):
            # Por defecto, delega completamente en service.get_paged
            items, total = await service.get_paged(params)
            return PaginatedOutput(items=items, total=total)

        # POST /
        @self.router.post(
            "/",
            response_model=self.output_schema,
            status_code=status.HTTP_201_CREATED,
        )
        async def create_item(
                payload: input_schema,
                service: TService = Depends(self.service_dependency),
        ):
            result = await service.create(payload)
            location = f"{self.router.prefix}/{result.id}"
            return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content=jsonable_encoder(self.output_schema.model_validate(result, from_attributes=True)),
                    headers={"Location": location}
            )

        # PUT /{id}
        @self.router.put(
            "/{item_id}",
            response_model=self.output_schema,
            status_code=status.HTTP_200_OK,
        )
        async def update_item(
                item_id: id_type,
                payload: update_schema,
                service: TService = Depends(self.service_dependency),
        ):
            # BaseService.update requiere un update_fn; el servicio concreto puede exponer
            # un método update_xxx que envuelva esta lógica, así que por defecto aquí
            # llamamos a un método estándar del service si lo define.
            if not hasattr(service, "update_item"):
                # Si el servicio no define un método de actualización “simple”,
                # se espera que el router concreto lo sobrescriba.
                raise NotImplementedError(
                    "El servicio debe implementar 'update_item' o el router debe definir su propia ruta PUT."
                )
            return await service.update_item(item_id, payload)  # type: ignore

        # DELETE /{id}
        @self.router.delete(
            "/{item_id}",
            status_code=status.HTTP_204_NO_CONTENT,
        )
        async def delete_item(
                item_id: id_type,
                service: TService = Depends(self.service_dependency),
        ):
            await service.delete(item_id)
            return None
