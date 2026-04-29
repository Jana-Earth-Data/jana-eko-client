"""Live-API integration tests for jana-eko-client.

These tests hit the **real** ``api-test.jana.earth`` endpoint and assert
the same wire-contract that the unit-level contract tests pin against
respx mocks. They are gated behind the ``integration`` pytest marker
and are normally skipped — the nightly GitHub Action (see
``.github/workflows/nightly-contract.yml``) runs them against a
service-account JWT.

Run locally with:

    EKO_TEST_USER=admin@jana.earth \\
    EKO_TEST_PASSWORD=$YOUR_PASSWORD \\
    pytest -m integration tests/integration/

If credentials are not supplied, all tests in this directory are
collected but skipped at runtime.
"""
