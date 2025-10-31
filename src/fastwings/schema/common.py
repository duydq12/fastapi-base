from typing import Any, Literal

from pydantic import BaseModel
from sqlalchemy import ColumnElement

QuerySortOperator = Literal["ASC", "DESC"]
OperatorType = Literal[
    "eq", "ne", "gt", "lt", "gte", "lte",
    "in", "nin", "like", "ilike", "starts", "ends", "cont",
    "isnull", "notnull",
]


class QueryFilter(BaseModel):
    field: ColumnElement[Any] | str
    operator: OperatorType
    value: Any


class QuerySort(BaseModel):
    field: ColumnElement[Any] | str
    order: QuerySortOperator


class ParsedRequestParams(BaseModel):
    page: int | None = None
    per_page: int | None = None
    limit: int | None = None
    offset: int | None = None

    fields: list[ColumnElement[Any] | str] = []
    filter: list[QueryFilter] = []
    or_: list[QueryFilter] = []
    sort: list[QuerySort] = []
    with_deleted: bool = False
