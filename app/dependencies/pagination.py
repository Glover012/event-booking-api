from typing import Annotated

from fastapi import Depends

from ..api.pagination import PaginationParams


### Dependencies ###
# Depends(), not Query(). FastAPI expands a Pydantic base model into its
# own query fields only while that model is the endpoint's only query parameter.
# Any additional query parameter will turn pagination params (page, per_page)
# into an unreachable ?pagination= param.
# Depends() resolves page and per_page as separate parameters from the
# start, so it allows to composes them with any additional query param. 
# With Depends() extra="forbid" doesn't work, so unknown parameters are
# silently ignored without 422 error.
pagination_dependency = Annotated[PaginationParams, Depends()]
