# Rate Limit Handling Implementation Plan

## Goal

Add first-class rate-limit handling to `eko-client` so callers get predictable behavior under `429 Too Many Requests` responses without having to reimplement retries and pacing in every notebook or script.

## Current State

- `_request_sync()` and `_request_async()` serialize access with locks, but they do not throttle outbound request rate.
- `_handle_response()` raises `EkoRateLimitError` on HTTP 429.
- `retry_after` is parsed from the response body when present, but it is not acted on.
- Heavy notebooks make many sequential requests in tight loops and can trigger rate limits even when run alone.

## Scope

Implement the following in `eko-client`:

- Configurable automatic retry on HTTP 429.
- Honor server-provided `retry_after` values when available.
- Fallback exponential backoff with jitter when `retry_after` is missing.
- Optional client-side request pacing to reduce burstiness.
- Clear documentation and tests for the new behavior.

## Non-Goals

- Rewriting notebook query strategies in this change.
- Introducing cross-process or distributed rate limiting.
- Guaranteeing avoidance of all rate limits for inefficient N+1 request patterns.

## Proposed Design

### 1. Add client configuration

Extend `BaseEkoClient.__init__()` with optional parameters such as:

- `max_retries: int = 3`
- `base_backoff_seconds: float = 1.0`
- `max_backoff_seconds: float = 30.0`
- `backoff_jitter_seconds: float = 0.5`
- `min_request_interval_seconds: float = 0.0`
- `retry_on_rate_limit: bool = True`

Design requirements:

- Preserve current behavior when retry is explicitly disabled.
- Keep defaults conservative and safe for notebook users.
- Apply the same config to sync and async request paths.

### 2. Centralize retry policy

Add small internal helpers in `client.py` to avoid duplicating policy logic:

- `_get_retry_delay(response, error_data, attempt_index) -> float`
- `_sleep_sync(delay_seconds) -> None`
- `_sleep_async(delay_seconds) -> Awaitable[None]`
- `_apply_request_pacing_sync() -> None`
- `_apply_request_pacing_async() -> Awaitable[None]`

Behavior:

- If the API returns `retry_after`, prefer it.
- Otherwise compute exponential backoff with bounded jitter.
- Clamp delays to `max_backoff_seconds`.
- Only retry 429 responses.
- Raise the original `EkoRateLimitError` after the retry budget is exhausted.

### 3. Retry loop in request methods

Refactor `_request_sync()` and `_request_async()` to:

1. Apply request pacing before each outbound call.
2. Send the request.
3. If the response is not 429, return `_handle_response(response)`.
4. If the response is 429 and retries remain:
   - parse the error payload,
   - compute delay,
   - wait,
   - retry.
5. If retries are exhausted, raise `EkoRateLimitError`.

Design notes:

- Keep locking semantics coherent so pacing state is thread-safe.
- Ensure async waits do not block the event loop.
- Avoid recursive retry flow; use iterative loops for clarity.

### 4. Track pacing state on the client

Add per-client state such as:

- `_last_request_monotonic`

Use `time.monotonic()` to implement a minimum interval between requests. This is not a full token bucket, but it is enough to smooth notebook bursts with low implementation risk.

### 5. Logging and visibility

Add debug-level logs for:

- detected 429s,
- chosen retry delay,
- retry attempt counts,
- pacing delays applied.

Avoid noisy info-level logging by default.

## Testing Plan

Add unit tests covering both sync and async clients:

- 429 with `retry_after` succeeds after one retry.
- 429 without `retry_after` uses exponential backoff.
- retries stop after `max_retries`.
- `retry_on_rate_limit=False` preserves immediate error behavior.
- `min_request_interval_seconds` delays consecutive requests.
- non-429 errors are not retried.

Implementation options:

- mock `httpx.Client.request` and `httpx.AsyncClient.request`
- patch sleep functions to avoid slow tests
- assert retry counts and delay selection

## Documentation Plan

Update `README.md` with:

- new rate-limit configuration options,
- example client construction for notebooks,
- guidance on when client retry is enough and when query patterns must be reduced.

Optionally add a short note to `TESTING.md` if new retry tests need special explanation.

## Rollout Plan

1. Implement retry and pacing internals in `client.py`.
2. Add sync and async tests.
3. Update README examples.
4. Validate against one heavy notebook and one lighter notebook.
5. Tune defaults if retries are too aggressive or too slow.

## Risks

- Retrying can hide inefficient notebook behavior if defaults are too permissive.
- Long retry windows may make notebooks feel hung if logging is insufficient.
- Holding locks during waits could reduce throughput if implemented carelessly.
- Different API endpoints may return `retry_after` in headers rather than JSON, which should be considered during implementation.

## Recommended Follow-Up After Client Work

Once the client behavior is in place, revisit heavy notebooks to reduce avoidable request volume:

- avoid repeated count-only calls in loops when aggregated endpoints already exist,
- avoid country-by-country sample estimation when a grouped endpoint can be added,
- add notebook-level pauses only where endpoint-specific limits still require them.
