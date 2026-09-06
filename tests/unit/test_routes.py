from collections import Counter

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute, _EffectiveRouteContext, _IncludedRouter

from app.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """File logging is disabled, or every run writes into LOG_DIR."""
    return create_app(enable_file_logging=False)


def _method_path_pairs(app: FastAPI) -> list[tuple[str, str]]:
    """
    Returns every (method, full path) pair included in API routing.
    """
    pairs: list[tuple[str, str]] = []

    for route in app.routes:
        # Only the routes that are included directly on app, like
        # app.post(...) etc. are of APIRoute instance
        if isinstance(route, APIRoute):
            if route.methods is not None:
                pairs += [(method, route.path) for method in route.methods]

        # The routes that come from an included APIRouter, so app.include_router(APIRouter)
        # are located inside _IncludedRouter instance. effective_candidates() function
        # returns _EffectiveRouteContext per endpoint, which contains path and method
        elif isinstance(route, _IncludedRouter):
            for candidate in route.effective_candidates():
                if isinstance(candidate, _EffectiveRouteContext):
                    pairs += [(method, candidate.path) for method in candidate.methods]

    return pairs


def test_method_path_pairs_returns(app):
    """
    Simple test whether _method_path_pairs acctualy returned anything.
    Used to avoid false positive empty result in the duplicate test.
    """

    assert _method_path_pairs(app)


def test_no_duplicate_method_path_pairs(app):
    """
    Test that no endpoint(methods, full path) inside the API is duplicated.

    A duplicated endpoint, so method + full path isn't reported by FastAPI,
    instead the first matching one is silently taken.
    """
    # Counter maps each hashable object to how many times it occurred in iterable
    duplicates = [
        pair for pair, count in Counter(_method_path_pairs(app)).items() if count > 1
    ]

    # Duplicates are attached to error message
    assert not duplicates, f"Duplicated routes: {duplicates}"
