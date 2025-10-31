from typing import Any, Generic, TypeVar, Sequence

from pydantic import BaseModel as PydanticBaseModel

from ..model import BaseModel
from ..repository.base_sql import SoftDeletableRepository
from ..schema.common import ParsedRequestParams
from ..utils.base_sql_serivce import convert_filter, convert_sort

ModelType = TypeVar("ModelType", bound=BaseModel)
RepoType = TypeVar("RepoType", bound=SoftDeletableRepository)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel)


class BaseSQLService(Generic[ModelType, RepoType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: RepoType):
        self.repository = repository

    async def get(self, *, obj_id: Any) -> ModelType:
        return await self.repository.get(obj_id=obj_id)

    async def get_by(self, parsed: ParsedRequestParams) -> ModelType:
        filters = convert_filter(self.repository.model, parsed)
        order_by = convert_sort(self.repository.model, parsed)
        return await self.repository.get_by(order_by=order_by, filters=filters)

    async def get_many(self, parsed: ParsedRequestParams) -> Sequence[ModelType]:
        filters = convert_filter(self.repository.model, parsed)
        order_by = convert_sort(self.repository.model, parsed)
        offset = parsed.offset or 0
        limit = parsed.limit or 10

        return await self.repository.get_many(offset=offset, limit=limit, order_by=order_by, filters=filters)

    async def get_all(self, parsed: ParsedRequestParams) -> Sequence[ModelType]:
        filters = convert_filter(self.repository.model, parsed)
        order_by = convert_sort(self.repository.model, parsed)
        return await self.repository.get_all(order_by=order_by, filters=filters)

    async def count(self, parsed: ParsedRequestParams) -> int:
        filters = convert_filter(self.repository.model, parsed)
        return await self.repository.count(filters=filters)

    async def exists(self, parsed: ParsedRequestParams) -> int:
        filters = convert_filter(self.repository.model, parsed)
        return await self.repository.exists(filters=filters)

    async def create(self, obj_in: CreateSchemaType, ) -> ModelType:
        return await self.repository.create(obj_in=obj_in)

    async def create_many(self, objs_in: Sequence[CreateSchemaType]) -> Sequence[ModelType]:
        return await self.repository.create_many(objs_in=objs_in)

    async def update(self, obj_id: Any, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        return await self.repository.update(obj_id=obj_id, obj_in=obj_in)

    async def update_many(self, parsed: ParsedRequestParams, values: dict[str, Any]) -> int:
        filters = convert_filter(self.repository.model, parsed)
        return await self.repository.update_many(filters=filters, values=values)

    async def delete(self, *, obj_id: Any) -> None:
        await self.repository.delete(obj_id=obj_id)

    async def delete_many(self, parsed: ParsedRequestParams) -> int:
        filters = convert_filter(self.repository.model, parsed)
        return await self.repository.delete_many(filters=filters)

    async def restore(self, obj_id: Any) -> ModelType:
        return await self.repository.restore(obj_id=obj_id)

    async def restore_many(self, parsed: ParsedRequestParams) -> int:
        filters = convert_filter(self.repository.model, parsed)
        return await self.repository.restore_many(filters=filters)

    async def hard_delete(self, obj_id: Any) -> None:
        await self.repository.hard_delete(obj_id=obj_id)

    async def hard_delete_many(self, parsed: ParsedRequestParams) -> int:
        filters = convert_filter(self.repository.model, parsed)
        return await self.repository.hard_delete_many(filters=filters)

    async def paginate(self, parsed: ParsedRequestParams) -> tuple[Sequence[ModelType], int]:
        filters = convert_filter(self.repository.model, parsed)
        order_by = convert_sort(self.repository.model, parsed)
        page = parsed.page or 1
        per_page = parsed.per_page or 20
        return await self.repository.paginate(page=page, per_page=per_page, order_by=order_by, filters=filters)

    async def upsert(
        self, obj_in: CreateSchemaType | UpdateSchemaType, match_fields: list[str]
    ) -> tuple[ModelType, bool]:
        return await self.repository.upsert(obj_in=obj_in, match_fields=match_fields)
