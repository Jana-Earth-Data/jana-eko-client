# Jana Eko Client - Python Client Library for Jana Earth Unified Environmental Data API

A Python client library for accessing the Jana Earth Unified Environmental Data API. This library provides easy access to environmental data from OpenAQ, Climate TRACE, and EDGAR sources through a clean, Pythonic interface.

## Features

- **Unified API Access**: Single interface for accessing data from multiple environmental data sources
- **Async & Sync Support**: Both synchronous and asynchronous methods for all API calls
- **Type-Safe**: Full type hints and Pydantic models for response validation
- **Thread-Safe**: Safe to use in multi-threaded and async environments
- **Two Client Types**:
  - `EkoUserClient`: End-user client (data access only, no job management)
  - `EkoAdminClient`: Admin client (full access including job management)
- **Production-Ready**: Comprehensive error handling, retry logic, and logging

## Installation

```bash
pip install jana-eko-client
```

Or install from source:

```bash
git clone https://github.com/Jana-Earth-Data/jana-eko-client
cd jana-eko-client
pip install -e .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git
```

## Quick Start

### Basic Usage (Synchronous)

```python
from eko_client import EkoUserClient

# Initialize with token
client = EkoUserClient(
    base_url="http://localhost:8000",
    token="your-token-here"
)

# Or login with credentials
client = EkoUserClient(
    base_url="http://localhost:8000",
    username="user",
    password="pass"
)

# Get unified data
data = client.get_data(
    sources=["openaq", "climatetrace"],
    location_bbox=[-74.1, 40.6, -73.9, 40.8],
    temporal_resolution="daily",
    quality_threshold=80
)

# Get correlations
correlations = client.get_correlations(
    sources=["openaq", "climatetrace"],
    parameters=["pm25", "co2"],
    correlation_type="spatial"
)
```

### Async Usage

```python
import asyncio
from eko_client import EkoUserClient

async def main():
    client = EkoUserClient(
        base_url="http://localhost:8000",
        token="your-token-here"
    )

    # Async data retrieval
    data = await client.get_data_async(
        sources=["openaq", "climatetrace"],
        location_bbox=[-74.1, 40.6, -73.9, 40.8]
    )

    # Concurrent requests
    results = await asyncio.gather(
        client.get_data_async(...),
        client.get_correlations_async(...),
        client.get_quality_async(...)
    )

    # Don't forget to close async client
    await client.close_async()

asyncio.run(main())
```

### Jupyter Notebook Usage

```python
from eko_client import EkoUserClient

eko = EkoUserClient(base_url="http://localhost:8000", token="...")

# In notebook cells
data = eko.get_data(
    sources=["openaq"],
    location_point=[-73.935, 40.730],
    radius_km=25
)

# Display results
import pandas as pd
df = pd.DataFrame(data['data']['air_quality'])
df.head()
```

## API Reference

### EkoUserClient

End-user client for accessing unified data APIs. Does not include job management endpoints.

#### Core Data Access

- `get_data()` - Get unified environmental data
- `get_aggregations()` - Get pre-computed temporal aggregations

#### Analytics & Intelligence

- `get_correlations()` - Cross-source correlation analysis
- `get_trends()` - Temporal trend analysis and forecasting

#### Quality & Monitoring

- `get_quality()` - Unified data quality insights
- `get_alerts()` - Quality-based intelligent alerts

#### Geographic & Spatial

- `get_geojson()` - Mapping-ready unified data in GeoJSON format
- `get_locations()` - Unified location data

#### Export & Bulk Access

- `create_export()` - Create bulk data export
- `get_export_status(export_id)` - Get export status
- `download_export(export_id)` - Download exported data

#### Metadata & Definitions

- `get_definitions()` - Unified definitions and metadata
- `get_parameter_definitions()` - Environmental parameter definitions
- `get_unit_definitions()` - Unit definitions and conversions
- `get_source_definitions()` - Data source information

#### System & Health

- `get_health()` - API health check
- `get_system_health()` - Comprehensive system health
- `get_summary()` - Platform summary

#### Source-Specific Endpoints

**OpenAQ:**
- `get_openaq_locations()` - Get OpenAQ locations
- `get_openaq_sensors()` - Get OpenAQ sensors
- `get_openaq_measurements()` - Get OpenAQ measurements
- `get_openaq_parameters()` - Get OpenAQ parameters

**Climate TRACE:**
- `get_climatetrace_sectors()` - Get Climate TRACE sectors
- `get_climatetrace_countries()` - Get Climate TRACE countries
- `get_climatetrace_assets()` - Get Climate TRACE assets
- `get_climatetrace_emissions()` - Get Climate TRACE emissions

**EDGAR:**
- `get_edgar_country_totals()` - Get EDGAR country totals
- `get_edgar_grid_emissions()` - Get EDGAR grid emissions
- `get_edgar_temporal_profiles()` - Get EDGAR temporal profiles
- `get_edgar_fasttrack()` - Get EDGAR fasttrack data

### EkoAdminClient

Admin client that extends `EkoUserClient` with job management capabilities.

#### Job Management

- `list_jobs()` - List all jobs
- `get_job(job_id)` - Get specific job
- `create_job(job_data)` - Create a new job
- `update_job(job_id, job_data)` - Update a job
- `delete_job(job_id)` - Delete a job
- `trigger_job(job_id)` - Trigger job execution
- `pause_job(job_id)` - Pause a job
- `resume_job(job_id)` - Resume a paused job
- `get_job_executions(job_id)` - Get executions for a job
- `get_job_stats(job_id)` - Get job statistics

#### Execution Management

- `list_executions()` - List all executions
- `get_execution(execution_id)` - Get specific execution
- `get_execution_logs(execution_id)` - Get execution logs
- `cancel_execution(execution_id)` - Cancel a running execution
- `retry_execution(execution_id)` - Retry a failed execution

#### Data Source Management

- `list_data_sources()` - List all data sources
- `get_data_source(source_id)` - Get specific data source
- `create_data_source(source_data)` - Create a new data source
- `update_data_source(source_id, source_data)` - Update a data source
- `delete_data_source(source_id)` - Delete a data source
- `check_data_source_health(source_id)` - Check data source health

#### System Management

- `get_management_health()` - Management API health check
- `get_management_summary()` - Management dashboard summary
- `get_database_performance()` - Database performance metrics
- `get_redis_performance()` - Redis performance metrics

## Error Handling

The library provides custom exceptions for better error handling:

```python
from eko_client import (
    EkoClientError,
    EkoAuthenticationError,
    EkoAPIError,
    EkoRateLimitError,
    EkoNotFoundError,
)

try:
    data = client.get_data(...)
except EkoAuthenticationError:
    print("Authentication failed")
except EkoRateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except EkoAPIError as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
except EkoClientError as e:
    print(f"Client error: {e.message}")
```

## Examples

### Get Air Quality and Emissions Data

```python
from eko_client import EkoUserClient

client = EkoUserClient(base_url="http://localhost:8000", token="...")

# Get daily data for NYC
data = client.get_data(
    sources=["openaq", "climatetrace"],
    location_bbox=[-74.1, 40.6, -73.9, 40.8],
    temporal_resolution="daily",
    quality_threshold=80,
    parameters=["pm25", "co2"]
)

print(f"Found {data['metadata']['total_records']} records")
```

### Analyze Correlations

```python
correlations = client.get_correlations(
    sources=["openaq", "climatetrace"],
    parameters=["pm25", "co2"],
    correlation_type="spatial",
    spatial_radius_km=10,
    statistical_tests=True
)

for corr in correlations.get('correlations', {}).get('spatial', []):
    print(f"Correlation: {corr['correlation_coefficient']:.2f}")
    print(f"P-value: {corr['p_value']:.4f}")
```

### Export Data

```python
# Create export
export = client.create_export(
    format="csv",
    query={
        "sources": ["openaq"],
        "location_bbox": [-74.1, 40.6, -73.9, 40.8],
        "date_from": "2023-01-01T00:00:00Z",
        "date_to": "2023-12-31T23:59:59Z"
    },
    compression="gzip"
)

export_id = export['export_id']

# Check status
import time
while True:
    status = client.get_export_status(export_id)
    if status['status'] == 'completed':
        break
    time.sleep(5)

# Download
data = client.download_export(export_id)
with open('export.csv.gz', 'wb') as f:
    f.write(data)
```

### Admin: Manage Jobs

```python
from eko_client import EkoAdminClient

admin = EkoAdminClient(base_url="http://localhost:8000", token="...")

# List all jobs
jobs = admin.list_jobs(status="active")

# Trigger a job
execution = admin.trigger_job(job_id=1)

# Monitor execution
execution_id = execution['id']
logs = admin.get_execution_logs(execution_id)
print(logs)
```

## Configuration

### Client Initialization Options

```python
client = EkoUserClient(
    base_url="http://localhost:8000",  # API base URL
    token="your-token",                 # Authentication token
    username="user",                    # Username (if no token)
    password="pass",                    # Password (if no token)
    timeout=30,                         # Request timeout in seconds
    verify_ssl=True                     # Verify SSL certificates
)
```

## Thread Safety

The client is thread-safe and can be used in multi-threaded environments. For async operations, use the `*_async` methods and ensure proper async context management.

## Context Manager Support

The client supports context manager protocol for automatic cleanup:

```python
with EkoUserClient(base_url="...", token="...") as client:
    data = client.get_data(...)
# Client is automatically closed
```

## Development

### Setup

```bash
git clone https://github.com/Jana-Earth-Data/jana-eko-client
cd jana-eko-client
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=eko_client --cov-report=term-missing

# Run a specific test file
pytest tests/test_jwt_auth.py

# Run a specific test class or method
pytest tests/test_pagination.py::TestFetchAllPagesSync::test_multi_page_with_count
```

### Test Suite

The test suite uses [respx](https://github.com/lundberg/respx) for HTTP mocking (no live API required) and [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) for async test support.

**300 tests, 99.8% coverage** across all modules:

| Module | Coverage |
|--------|----------|
| `client.py` (BaseEkoClient) | 99% |
| `user_client.py` (EkoUserClient) | 100% |
| `admin_client.py` (EkoAdminClient) | 100% |
| `jwt_auth.py` (JwtAuthMixin) | 100% |
| `auth.py` (AuthMixin) | 100% |
| `sync_wrapper.py` | 100% |
| `exceptions.py` | 100% |
| `models.py` | 100% |
| `utils.py` | 100% |

### Code Style

```bash
# Format with black
black eko_client/ tests/

# Lint with ruff
ruff check eko_client/ tests/

# Type check with mypy
mypy eko_client/
```

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0
- typing-extensions >= 4.5.0

---

## Refactoring History

This library has undergone significant refactoring to improve code quality, maintainability, and developer experience. Below is a comprehensive history of all major refactoring work:

### Version 0.2.0 - Repository Extraction (2026-03-02)

**Changes:**
- Extracted eko-client-python as standalone repository `jana-eko-client`
- Renamed package from `eko-client` to `jana-eko-client`
- Updated organization to `Jana-Earth-Data`
- Updated contact information to `contact@jana.earth`
- Version bumped from 0.1.0 to 0.2.0

**Rationale:**
The client library is now mature enough to be maintained as a standalone package, enabling:
- Independent versioning and release cycles
- Easier distribution via PyPI
- Better separation of concerns between API server and client library
- Simpler dependency management for external users

---

### Refactor #1: Sync/Async Wrapper Elimination (2026-02-28)
**Commit**: `20cc258`

**Problem:**
The codebase contained massive duplication between async and sync methods. Every async method had a corresponding sync wrapper method, leading to:
- 691 lines of duplicate boilerplate code
- Maintenance burden (changes needed in two places)
- Risk of sync/async inconsistencies
- Harder to add new methods

**Solution:**
Created `sync_wrapper.py` with an `@auto_sync_wrapper` decorator that automatically generates sync methods from async methods at runtime:

**Files Changed:**
- Created `eko_client/sync_wrapper.py` (121 lines)
- Refactored `eko_client/admin_client.py`: 569 → 419 lines (150 lines removed, 26% reduction)
- Refactored `eko_client/user_client.py`: 1,475 → 934 lines (541 lines removed, 37% reduction)

**Impact:**
- **Total: 691 lines of duplicate code eliminated**
- Single source of truth (only async methods need to be defined)
- Easier to add new methods (just define async version)
- 100% backward compatible
- Preserves signatures, docstrings, and type annotations

**Technical Details:**
```python
@auto_sync_wrapper
class EkoUserClient:
    # Define async method once
    async def get_data_async(self, ...):
        """Get unified data"""
        ...

    # Sync wrapper auto-generated at runtime
    # def get_data(self, ...):
    #     return asyncio.run(self.get_data_async(...))
```

---

### Refactor #2: Exception Handling Improvements (2026-02-28)
**Commit**: `f4ad44c`

**Problem:**
The client used bare `except:` clauses that caught all exceptions indiscriminately, hiding errors and making debugging difficult.

**Solution:**
Fixed 3 broad exception handlers in `eko_client/client.py`:

1. **Line 252**: JSON parsing errors
   - Before: `except Exception:`
   - After: `except (json.JSONDecodeError, ValueError):`
   - Added warning logging for parse failures

2. **Line 260**: Logout errors
   - Before: `except Exception:`
   - After: `except httpx.HTTPError:`
   - Added warning logging for logout failures

3. **Line 314**: Request errors
   - Before: `except Exception:`
   - After: `except httpx.HTTPError:`
   - Proper error propagation

**Impact:**
- Better error visibility and debugging
- Proper error handling and logging
- Prevents hiding critical errors
- Part of larger effort to fix 19 bare except clauses across the Jana platform

---

### Enhancement: Async Query Architecture Design (2026-02-12)
**Commit**: `f6ce63e`

**Changes:**
- Added comprehensive async query architecture design document
- Located in `async_design_docs/Async_Query_Architecture_Design.md`
- Documents best practices for async API queries
- Provides patterns for concurrent data fetching

**Impact:**
- Better documentation for async usage patterns
- Guidance for developers on optimal async query strategies
- Examples of concurrent request patterns

---

### Enhancement: Documentation & Pip Library Guide (2026-02-07)
**Commit**: `f90b397`

**Changes:**
- Added `pip_installable_library_from_repo_for_dummies.md`
- Complete guide for installing library from GitHub
- Documentation for local development setup
- Integration instructions

**Impact:**
- Easier onboarding for new developers
- Clear installation instructions
- Reduced friction for library adoption

---

### Initial Release: Climate TRACE Integration (2026-01-02)
**Commit**: `3c1a322`

**Changes:**
- Added Climate TRACE temporal aggregations
- Implemented chunked query support
- Improved error handling for large datasets

---

### Foundation: Major Platform Update (2025-11-13)
**Commit**: `f29de9c`

**Changes:**
- Initial client library creation
- EDGAR integration
- OpenAQ support
- Core architecture and patterns established

---

## Development Philosophy

This library follows these key principles:

1. **Single Source of Truth**: Use decorators and metaprogramming to eliminate duplication
2. **Type Safety**: Full type hints for better IDE support and error detection
3. **Async-First**: Design async methods first, generate sync wrappers automatically
4. **Proper Error Handling**: Specific exception types, never bare except clauses
5. **Comprehensive Documentation**: Every refactor documented with rationale
6. **Backward Compatibility**: Maintain API stability across refactors

---

## Migration Guide

### From eko-client (v0.1.0) to jana-eko-client (v0.2.0)

**Package Name Change:**
```bash
# Old
pip install eko-client

# New
pip install jana-eko-client
```

**Import Statements:** (No Change)
```python
# Imports remain the same
from eko_client import EkoUserClient, EkoAdminClient
```

**API Compatibility:**
All public APIs remain 100% compatible. No code changes required beyond updating the package name.

---

## License

MIT License

## Support

For issues, questions, or contributions, please visit:
- **GitHub**: https://github.com/Jana-Earth-Data/jana-eko-client
- **Documentation**: https://docs.jana.earth
- **Email**: contact@jana.earth

## Contributing

We welcome contributions! Please see our contributing guidelines and code of conduct.

## Acknowledgments

Built with love by the Jana Earth Data team to make environmental data accessible to everyone.
