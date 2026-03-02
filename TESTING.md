# Testing jana-eko-client

This document explains how to test the `jana-eko-client` library.

## Quick Start

### 1. Install the Library

```bash
# From GitHub (recommended for testing)
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git

# Or for development
git clone https://github.com/Jana-Earth-Data/jana-eko-client.git
cd jana-eko-client
pip install -e .
```

### 2. Set Up Credentials

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
JANA_API_URL=https://api-dev.jana.earth
JANA_USERNAME=your-username
JANA_PASSWORD=your-password
```

**Security Note**: The `.env` file is in `.gitignore` and will NOT be committed.

### 3. Run the Test Suite

#### Option A: Jupyter Notebook (Recommended)

```bash
# Install Jupyter if needed
pip install jupyter

# Export environment variables
export $(cat .env | xargs)

# Launch Jupyter
jupyter notebook
```

Open `jana_eko_client_test_suite.ipynb` and run all cells.

#### Option B: Python Script

Convert the notebook to a script and run:

```bash
# Export environment variables
export $(cat .env | xargs)

# Run tests
jupyter nbconvert --to python jana_eko_client_test_suite.ipynb
python jana_eko_client_test_suite.py
```

## Test Coverage

The test suite validates:

### Authentication & Health
- ✅ Client initialization with username/password
- ✅ User info retrieval
- ✅ API health checks
- ✅ System health and platform summary

### OpenAQ Endpoints
- ✅ Parameters, locations, sensors, measurements
- ✅ Country and parameter filtering
- ✅ Statistics and aggregations
- ⚠️ Some aggregations may timeout (large datasets)

### Climate TRACE Endpoints
- ✅ Sectors, countries, assets, emissions
- ✅ Country filtering
- ✅ Totals and sector/country aggregations
- ⚠️ Date range queries may timeout

### EDGAR Endpoints
- ✅ Country totals, temporal profiles, FastTrack
- ✅ Grid emissions and air pollutant data
- ⚠️ Full grid listings may timeout

### ESG Unified Endpoints
- ✅ Definitions (parameters, units, sources)
- ✅ Unified data access across sources
- ✅ Locations and sectors
- ⚠️ Cross-source analytics may timeout (materialized views)

### Export Functionality
- ✅ Create async export
- ✅ Check export status
- ✅ Download completed exports

### Error Handling
- ✅ 404 Not Found errors
- ✅ Authentication errors
- ✅ Custom exception types

## Expected Results

### Pass Rate
- **Target**: 95%+ pass rate
- **Common failures**: Timeouts on dev environment (expected)

### Timeouts
Some endpoints may timeout on the dev environment due to:
- Large dataset aggregations (133M+ OpenAQ measurements)
- Materialized view recreation (recent ingestion work)
- ALB idle timeout (30s) < query time on t3.small instance

**This is expected and documented in the test output.**

### Response Times
- **Average**: 500-1500ms
- **Slow queries**: 2000-5000ms (aggregations)
- **Timeouts**: 30000ms+ (ALB timeout)

## Test Environments

### Development (api-dev.jana.earth)
- Credentials: `dev-user` account
- Dataset: Production snapshot
- Instance: t3.small (limited resources)
- Timeouts: Expected on heavy aggregations
- **Note**: Both sync and async methods work correctly

### Production (api.jana.earth)
- Credentials: Your production account
- Dataset: Full production data
- Instance: Larger instance size
- Performance: Better than dev

## Troubleshooting

### "ModuleNotFoundError: No module named 'eko_client'"
```bash
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git
```

### "Authentication failed"
- Check username/password in `.env`
- Verify API URL is correct
- Test credentials with `curl`:
  ```bash
  curl -X POST https://api-dev.jana.earth/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username":"your-user","password":"your-pass"}'
  ```

### "Connection timeout"
- Check network connectivity
- Verify API is accessible: `curl https://api-dev.jana.earth/health/`
- Some endpoints timeout on dev (expected)

### "Invalid token" after some time
- Tokens expire after inactivity
- Re-run the authentication cell
- Or create a new client instance

## Manual Testing

For quick manual tests (both sync and async methods work):

### Synchronous (Traditional Python):

```python
from eko_client import EkoUserClient

# Initialize
client = EkoUserClient(
    base_url="https://api-dev.jana.earth",
    username="dev-user",
    password="your-password"
)

# Multiple sync calls work correctly
health = client.get_health()
locations = client.get_openaq_locations(country_codes="USA", limit=5)
print(f"Found {len(locations['results'])} locations")

# Test with error handling
from eko_client.exceptions import EkoNotFoundError

try:
    client.get_openaq_locations(location_id=999999)
except EkoNotFoundError:
    print("Location not found (expected)")

# Clean up (optional)
client.close_sync_loop()
```

### Asynchronous (Async/Await):

```python
import asyncio
from eko_client import EkoUserClient

async def main():
    client = EkoUserClient(
        base_url="https://api-dev.jana.earth",
        username="dev-user",
        password="your-password"
    )

    # Multiple async calls work perfectly
    health = await client.get_health_async()
    locations = await client.get_openaq_locations_async(
        country_codes="USA", limit=5
    )
    print(f"Found {len(locations['results'])} locations")

    await client.close_async()

asyncio.run(main())
```

## Continuous Integration

To run tests in CI/CD:

```bash
# Install
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git

# Set credentials (from secrets)
export JANA_API_URL="https://api-dev.jana.earth"
export JANA_USERNAME="$CI_USERNAME"
export JANA_PASSWORD="$CI_PASSWORD"

# Run tests
jupyter nbconvert --to python --execute jana_eko_client_test_suite.ipynb
```

## Contributing

When adding new client methods:

1. Add corresponding tests to the notebook
2. Test against dev environment
3. Document expected behavior and timeouts
4. Update this README if needed

## Support

For issues:
- **GitHub Issues**: https://github.com/Jana-Earth-Data/jana-eko-client/issues
- **Email**: contact@jana.earth
- **Documentation**: https://docs.jana.earth
