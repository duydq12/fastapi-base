from typing import Any, Sequence

from sqlalchemy import ColumnElement, or_

from fastwings.model import BaseModel
from ..schema.common import QueryFilter, ParsedRequestParams, QuerySort

OPERATORS = {
    'eq': lambda col, val: col == val,
    'ne': lambda col, val: col != val,
    'gt': lambda col, val: col > val,
    'lt': lambda col, val: col < val,
    'gte': lambda col, val: col >= val,
    'lte': lambda col, val: col <= val,
    'in': lambda col, val: col.in_(val),
    'nin': lambda col, val: col.not_in(val),
    'like': lambda col, val: col.like(val),
    'ilike': lambda col, val: col.ilike(val),
    'starts': lambda col, val: col.like(f"{val}%"),
    'ends': lambda col, val: col.like(f"%{val}"),
    'cont': lambda col, val: col.like(f"%{val}%"),
    'isnull': lambda col, _: col.is_(None),
    'notnull': lambda col, _: col.is_not(None),
}


def __get_column(
    model: BaseModel,
    query_item: QueryFilter | QuerySort,
):
    # Navigate dot-notation (e.g., "profile.email")
    column = model
    for part in query_item.field.split("."):
        if not hasattr(column, part):
            raise ValueError(f"Invalid field: {query_item.field}")
        column = getattr(column, part)
    return column


def __build_filter_condition(
    model: BaseModel,
    filter_item: QueryFilter,
) -> ColumnElement[bool]:
    column = __get_column(model, filter_item)
    op = filter_item.operator
    val = filter_item.value
    if op not in OPERATORS:
        raise ValueError(f"Unsupported operator: {op}")
    return OPERATORS[op](column, val)


def convert_sort(
    model: BaseModel,
    parsed: ParsedRequestParams,
) -> Sequence[ColumnElement[Any]]:
    """Parse all sorts into order_by list."""
    order_by: list[ColumnElement[Any]] = []

    for s in parsed.sort:
        column = __get_column(model, s)
        if s.order.upper() == "ASC":
            order_by.append(column.asc())
        elif s.order.upper() == "DESC":
            order_by.append(column.desc())
        else:
            raise ValueError(f"Unsupported sort order: {s.order}")

    return order_by


def convert_or(
    model: BaseModel,
    parsed: ParsedRequestParams,
) -> ColumnElement[bool]:
    """Parse all OR filters into condition."""
    or_conditions: list[ColumnElement[bool]] = []

    for f in parsed._or:
        or_conditions.append(__build_filter_condition(model, f))

    return or_(*or_conditions)


def convert_filter(
    model: BaseModel,
    parsed: ParsedRequestParams,
) -> Sequence[ColumnElement[bool]]:
    """Parse all filters + soft delete into condition list."""
    filters: list[ColumnElement[bool]] = []

    # Soft delete
    if not parsed.with_deleted and hasattr(model, "is_deleted"):
        filters.append(getattr(model, "is_deleted").is_(False))

    for f in parsed.filter:
        filters.append(__build_filter_condition(model, f))

    return filters
