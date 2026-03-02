# jana-eko-client Test Results

**Date**: 2026-03-02
**Version**: 0.2.0
**Environment**: macOS, Python 3.9, DEV API (https://api-dev.jana.earth)

## Summary

✅ **Async Methods**: Working perfectly
⚠️ **Sync Methods**: Known issue with multiple sequential calls
✅ **Authentication**: Working
✅ **API Endpoints**: All tested endpoints accessible

---

## Async Methods Testing

**Status**: ✅ **PASS** - All async methods work correctly

### Test Results:

```
✓ get_health_async() - Multiple calls successful
✓ get_openaq_parameters_async() - 30 parameters retrieved
✓ get_openaq_locations_async() - 100 locations retrieved
✓ get_climatetrace_sectors_async() - 26 sectors retrieved
✓ close_async() - Clean shutdown successful
```

### Usage Example:

```python
import asyncio
from eko_client import EkoUserClient

async def main():
    client = EkoUserClient(
        base_url="https://api-dev.jana.earth",
        username="dev-user",
        password="your-password",
        timeout=60
    )

    # Multiple async calls work perfectly
    health = await client.get_health_async()
    params = await client.get_openaq_parameters_async()
    sectors = await client.get_climatetrace_sectors_async()

    await client.close_async()

asyncio.run(main())
```

**Recommendation**: ✅ **Use async methods for production code**

---

## Sync Methods Testing

**Status**: ⚠️ **ISSUE FOUND** - Multiple sequential sync calls fail

### Problem:

The sync wrapper uses `asyncio.run()` which creates and closes an event loop for each call. This causes issues with httpx's connection pooling:

1. ✅ **First call**: Works perfectly
2. ❌ **Second call**: Fails with `RuntimeError: Event loop is closed`

### Error:

```
RuntimeError: Event loop is closed
```

This occurs because:
- `asyncio.run()` closes the event loop after each call
- httpx AsyncClient maintains persistent connections
- Those connections try to cleanup on a closed loop

### Workaround:

Create a new client instance for each sync call:

```python
# ❌ BROKEN: Multiple calls with same instance
client = EkoUserClient(...)
health1 = client.get_health()  # ✓ Works
health2 = client.get_health()  # ✗ Fails - event loop closed

# ✅ WORKAROUND: New instance per call (not ideal)
client1 = EkoUserClient(...)
health1 = client1.get_health()  # ✓ Works

client2 = EkoUserClient(...)
health2 = client2.get_health()  # ✓ Works
```

### Root Cause:

**Location**: `eko_client/sync_wrapper.py:48`

```python
def sync_wrapper(self, *args, **kwargs):
    return asyncio.run(async_method(self, *args, **kwargs))
```

The `asyncio.run()` pattern doesn't work well for stateful clients with persistent connections.

### Recommended Fix (Future):

Replace `asyncio.run()` with a persistent event loop:

```python
def _create_sync_wrapper(async_method: Callable) -> Callable:
    @wraps(async_method)
    def sync_wrapper(self, *args, **kwargs):
        if not hasattr(self, '_sync_loop'):
            self._sync_loop = asyncio.new_event_loop()

        return self._sync_loop.run_until_complete(
            async_method(self, *args, **kwargs)
        )
    return sync_wrapper
```

Or use `nest_asyncio` to allow nested event loops.

---

## Authentication Testing

**Status**: ✅ **PASS**

```
✓ Username/password authentication works
✓ Token retrieved successfully (1696ms)
✓ get_user_info() returns correct user data
✓ No AWS dependencies (no boto3, no SSM)
```

---

## API Endpoint Coverage

### OpenAQ Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `get_openaq_parameters_async()` | ✅ PASS | 30 parameters |
| `get_openaq_locations_async()` | ✅ PASS | 100 locations |
| `get_openaq_measurements_async()` | ✅ PASS | Pagination works |
| `get_openaq_measurements_totals_async()` | ✅ PASS | Aggregation works |

### Climate TRACE Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `get_climatetrace_sectors_async()` | ✅ PASS | 26 sectors |
| `get_climatetrace_countries_async()` | ✅ PASS | Countries retrieved |
| `get_climatetrace_emissions_async()` | ✅ PASS | Emissions data works |
| `get_climatetrace_emissions_totals_async()` | ✅ PASS | Aggregation works |

### EDGAR Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `get_edgar_country_totals_async()` | ✅ PASS | 100 records |
| `get_edgar_fasttrack_async()` | ✅ PASS | Data retrieved |
| `get_edgar_temporal_profiles_async()` | ✅ PASS | Profiles work |

### ESG Unified Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `get_health_async()` | ✅ PASS | Health check works |
| `get_system_health_async()` | ✅ PASS | System status |
| `get_definitions_async()` | ✅ PASS | Definitions retrieved |
| `get_parameter_definitions_async()` | ✅ PASS | Parameters work |
| `get_unit_definitions_async()` | ✅ PASS | Units retrieved |
| `get_source_definitions_async()` | ✅ PASS | Sources work |

---

## Recommendations

### For Production Use:

1. ✅ **Use async methods** (`*_async()`)
   - Full functionality
   - Proper connection pooling
   - No event loop issues

2. ⚠️ **Avoid sync methods** until fixed
   - Single calls work
   - Multiple calls fail
   - Workaround: recreate client per call (inefficient)

3. ✅ **Use in async context** (FastAPI, aiohttp, etc.)
   ```python
   from fastapi import FastAPI
   from eko_client import EkoUserClient

   app = FastAPI()
   client = EkoUserClient(...)  # Create once

   @app.get("/health")
   async def health():
       return await client.get_health_async()
   ```

### For Development:

```bash
# Install
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git

# Test async methods
python3 test_async_client.py
```

---

## Files Tested

- ✅ `eko_client/__init__.py` - Exports work
- ✅ `eko_client/user_client.py` - User client works
- ✅ `eko_client/auth.py` - Authentication works
- ✅ `eko_client/client.py` - Base client works
- ⚠️ `eko_client/sync_wrapper.py` - Has known issue

---

## Next Steps

### High Priority:

1. **Fix sync wrapper** for multiple sequential calls
   - Option A: Persistent event loop per instance
   - Option B: Use `nest_asyncio`
   - Option C: Document sync methods as "single-call only"

2. **Update test notebook** to use only async methods
   - Remove sync calls
   - Use `asyncio.run()` at notebook level

3. **Update documentation** to clarify async vs sync usage

### Medium Priority:

1. Add unit tests for sync wrapper
2. Add integration tests with real API
3. Test timeout handling
4. Test error handling edge cases

---

## Conclusion

**The jana-eko-client library core functionality works correctly:**
- ✅ Authentication works
- ✅ All API endpoints accessible
- ✅ Async methods work perfectly
- ⚠️ Sync methods need fix for multiple calls

**Recommended usage**: Use async methods (`*_async()`) in production until sync wrapper is fixed.

**Impact**: Low - Most Python async frameworks (FastAPI, aiohttp, etc.) work better with async methods anyway.
