# Sample Notebooks

This directory contains example Jupyter notebooks demonstrating how to use the `jana-eko-client` library for various environmental data analysis tasks.

## Setup

### 1. Install the Client

```bash
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git
```

### 2. Set Credentials

Create a `.env` file in your working directory or export environment variables:

```bash
export JANA_API_URL="https://api-dev.jana.earth"
export JANA_USERNAME="your-username"
export JANA_PASSWORD="your-password"
```

### 3. Launch Jupyter

```bash
# Export environment variables first
export $(cat .env | xargs)  # If using .env file

# Launch Jupyter
jupyter notebook
```

## Standard Setup Pattern

All notebooks use this standard setup pattern:

```python
import os
import warnings
from eko_client import EkoUserClient

# Suppress Jupyter introspection warnings
warnings.filterwarnings('ignore', message='coroutine.*was never awaited')

# Get credentials from environment
BASE_URL = os.environ.get("JANA_API_URL", "https://api-dev.jana.earth")
USERNAME = os.environ.get("JANA_USERNAME")
PASSWORD = os.environ.get("JANA_PASSWORD")

if not PASSWORD:
    from getpass import getpass
    PASSWORD = getpass(f"Enter password for {USERNAME}: ")

# Initialize client
client = EkoUserClient(
    base_url=BASE_URL,
    username=USERNAME,
    password=PASSWORD,
    timeout=60
)

# Test connection
health = client.get_health()
print(f"✅ Connected: {health.get('status')}")
```

## Key Features

- **No AWS Dependencies**: Uses simple username/password authentication
- **No sys.path Manipulation**: Import directly from `eko_client`
- **Automatic Jupyter Support**: Works seamlessly in Jupyter notebooks with automatic `nest_asyncio` handling
- **Clean Credentials**: Uses environment variables, never hardcoded

## Available Notebooks

### Data Analysis & Summaries

1. **`openaq_data_summary.ipynb`** - Comprehensive OpenAQ air quality data analysis
   - Platform statistics and totals
   - Parameter and country distributions
   - Temporal trends
   - Data quality analysis
   - Automated report generation

2. **`climatetrace_data_summary.ipynb`** - Climate TRACE emissions data analysis
   - Global emissions overview
   - Sector and country breakdowns
   - Asset-level analysis
   - Temporal trends

3. **`nepal_data_analysis.ipynb`** - Regional environmental data analysis for Nepal
   - Multi-source data integration (OpenAQ, Climate TRACE, EDGAR)
   - Air quality trends
   - Emissions analysis
   - Regional comparisons

### Research & Investment

4. **`esg_investment_intelligence.ipynb`** - ESG investment analysis
   - Environmental risk assessment
   - Multi-source data correlation
   - Investment recommendations
   - Portfolio analysis

5. **`climate_science_policy_esg_research_agenda.ipynb`** - Research framework
   - Climate science integration
   - Policy analysis
   - ESG research workflows
   - Data-driven insights

## Tips

### Working with Large Datasets

Some notebooks query large datasets. If you encounter timeouts:

1. **Reduce date ranges**: Use `date_from` and `date_to` parameters
2. **Limit results**: Use `limit` parameter (e.g., `limit=1000`)
3. **Use aggregations**: Use totals/statistics endpoints instead of raw data

```python
# Good: Use aggregations
totals = client.get_openaq_measurements_totals()

# Avoid: Fetching all records
all_records = client.get_openaq_measurements(limit=100000)  # May timeout
```

### Pagination Example

```python
def fetch_all_pages(client_method, **kwargs):
    """Fetch all pages with pagination."""
    all_results = []
    offset = 0
    limit = kwargs.get('limit', 1000)

    while True:
        response = client_method(offset=offset, limit=limit, **kwargs)
        results = response.get('results', [])
        if not results:
            break

        all_results.extend(results)
        offset += len(results)

        # Check if we've fetched everything
        if 'count' in response and len(all_results) >= response['count']:
            break

    return all_results
```

### Async vs Sync Methods

The client library provides both sync and async methods:

```python
# Synchronous (works in Jupyter out of the box)
health = client.get_health()
params = client.get_openaq_parameters()

# Asynchronous (for async frameworks like FastAPI)
async def get_data():
    health = await client.get_health_async()
    params = await client.get_openaq_parameters_async()
```

**For Jupyter notebooks**: Use the synchronous methods (without `_async` suffix). The library automatically handles event loop compatibility.

## Troubleshooting

### "Module not found: eko_client"

```bash
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git
```

### "Authentication failed"

1. Check your credentials in `.env` or environment variables
2. Verify the API URL is correct
3. Ensure the API service is running

### "Connection timeout"

1. Check network connectivity
2. Verify the API is accessible
3. Try reducing the dataset size with `limit` parameter
4. Use aggregation endpoints instead of raw data

### Import Errors

Restart the Jupyter kernel after installing the client:
- Kernel → Restart Kernel

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/Jana-Earth-Data/jana-eko-client/issues
- **Documentation**: https://docs.jana.earth
- **Email**: contact@jana.earth
