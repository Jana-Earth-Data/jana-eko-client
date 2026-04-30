"""Contract tests for jana-eko-client.

These tests pin the wire contract between EkoUserClient methods and the
Jana API. They use ``respx`` to mock HTTP responses and assert on three
things per method:

1. **URL** — the endpoint path the client builds.
2. **Query params** — the exact set of param names and values that go
   on the wire (so silent kwarg renames break tests, not user data).
3. **Response shape** — the client correctly parses paginated and
   flat-dict responses.

Fixtures are seeded from the Step-7 live-probe artifact at
``engineering-documents/jana/docs/operations_docs/eko_client_audit_20260424_artifacts/eko_step7_probe_results_20260428.json``
so the contract is grounded in what the live API actually returns.

Run with:

    pytest tests/contract/

These run as part of the regular unit-test suite (no ``-m`` marker
required). For the live-API counterpart see ``tests/integration/``.
"""
