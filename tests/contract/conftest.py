"""Conftest for contract tests.

Re-exports the harness so individual test files can import directly:

    from tests.contract.conftest import STEP7_FIXTURES, make_paginated_response, assert_query_params

The fixtures themselves (``mock_api``, ``user_client_dual``) are inherited
from ``tests/conftest.py``.
"""

from ._harness import (  # noqa: F401  (re-export)
    STEP7_FIXTURES,
    assert_query_params,
    make_paginated_response,
)
