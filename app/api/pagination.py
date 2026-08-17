import math

from typing import Generic, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field


ITEM = TypeVar("ITEM")


class PaginationParams(BaseModel):
    """
    Query parameters for every endpoint that is listing 
    many resources from db, like: events.
    """

    model_config = ConfigDict(
        extra="forbid"
        ) # Unknown query parameters are rejected

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """
        Translates the page number into the row offset, required
        by SQL query.
        """
        return (self.page - 1) * self.per_page


class Page(BaseModel, Generic[ITEM]):
    """
    One page of results. Total counts every row in db matching the query,
    not the rows returned, so the client can work out the number of pages
    and render controls.
    """

    items: list[ITEM]
    page: int
    pages: int
    total: int

    @classmethod
    def create(
        cls,
        items: list,
        total: int,
        pagination: PaginationParams,
    ) -> Self:

        return cls(
            items=items,
            page=pagination.page,
            total=total,
            pages=math.ceil(total / pagination.per_page),
        )
