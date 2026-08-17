from typing import Annotated

from fastapi import Query

from ..api.pagination import PaginationParams


### Dependencies ###
# Query() adds query parameters for pagination, page + per_page(def.20)
pagination_dependency = Annotated[PaginationParams, Query()]
