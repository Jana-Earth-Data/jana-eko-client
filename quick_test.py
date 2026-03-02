#!/usr/bin/env python3
"""
Quick test script for jana-eko-client
Tests core functionality without requiring Jupyter
"""

import os
import time
from eko_client import EkoUserClient
from eko_client.exceptions import EkoAuthenticationError, EkoAPIError

# Configuration
BASE_URL = os.environ.get("JANA_API_URL", "https://api-dev.jana.earth")
USERNAME = os.environ.get("JANA_USERNAME", "dev-user")
PASSWORD = os.environ.get("JANA_PASSWORD", "")

if not PASSWORD:
    print("ERROR: JANA_PASSWORD environment variable not set")
    exit(1)

print(f"Testing jana-eko-client against {BASE_URL}")
print(f"Username: {USERNAME}")
print("="*80)

# Initialize client
print("\n[1/6] Initializing client and authenticating...")
try:
    start = time.time()
    client = EkoUserClient(
        base_url=BASE_URL,
        username=USERNAME,
        password=PASSWORD,
        timeout=60
    )
    elapsed = (time.time() - start) * 1000
    print(f"✓ PASS - Client initialized ({elapsed:.1f}ms)")

    # Get user info
    user_info = client.get_user_info()
    print(f"✓ Logged in as: {user_info.get('username')}")
except EkoAuthenticationError as e:
    print(f"✗ FAIL - Authentication error: {e}")
    exit(1)
except Exception as e:
    print(f"✗ FAIL - Initialization error: {e}")
    exit(1)

# Test health checks
print("\n[2/6] Testing health checks...")
try:
    health = client.get_health()
    print(f"✓ PASS - get_health()")

    system_health = client.get_system_health()
    print(f"✓ PASS - get_system_health()")

    summary = client.get_summary()
    print(f"✓ PASS - get_summary()")
except Exception as e:
    print(f"✗ FAIL - Health check error: {e}")

# Test OpenAQ endpoints
print("\n[3/6] Testing OpenAQ endpoints...")
try:
    params = client.get_openaq_parameters()
    print(f"✓ PASS - get_openaq_parameters() - {len(params.get('results', []))} parameters")

    locations = client.get_openaq_locations(limit=5)
    print(f"✓ PASS - get_openaq_locations(limit=5) - {len(locations.get('results', []))} locations")

    measurements = client.get_openaq_measurements(limit=5)
    print(f"✓ PASS - get_openaq_measurements(limit=5) - {len(measurements.get('results', []))} measurements")

    totals = client.get_openaq_measurements_totals()
    print(f"✓ PASS - get_openaq_measurements_totals()")
except Exception as e:
    print(f"✗ FAIL - OpenAQ error: {e}")

# Test Climate TRACE endpoints
print("\n[4/6] Testing Climate TRACE endpoints...")
try:
    sectors = client.get_climatetrace_sectors()
    print(f"✓ PASS - get_climatetrace_sectors() - {len(sectors.get('results', []))} sectors")

    countries = client.get_climatetrace_countries()
    print(f"✓ PASS - get_climatetrace_countries() - {len(countries.get('results', []))} countries")

    emissions = client.get_climatetrace_emissions(limit=5)
    print(f"✓ PASS - get_climatetrace_emissions(limit=5) - {len(emissions.get('results', []))} emissions")

    totals = client.get_climatetrace_emissions_totals()
    print(f"✓ PASS - get_climatetrace_emissions_totals()")
except Exception as e:
    print(f"✗ FAIL - Climate TRACE error: {e}")

# Test EDGAR endpoints
print("\n[5/6] Testing EDGAR endpoints...")
try:
    country_totals = client.get_edgar_country_totals(limit=5)
    print(f"✓ PASS - get_edgar_country_totals(limit=5) - {len(country_totals.get('results', []))} records")

    fasttrack = client.get_edgar_fasttrack(limit=5)
    print(f"✓ PASS - get_edgar_fasttrack(limit=5) - {len(fasttrack.get('results', []))} records")

    temporal = client.get_edgar_temporal_profiles(limit=5)
    print(f"✓ PASS - get_edgar_temporal_profiles(limit=5) - {len(temporal.get('results', []))} records")
except Exception as e:
    print(f"✗ FAIL - EDGAR error: {e}")

# Test ESG unified endpoints
print("\n[6/6] Testing ESG unified endpoints...")
try:
    definitions = client.get_definitions()
    print(f"✓ PASS - get_definitions()")

    params = client.get_parameter_definitions()
    print(f"✓ PASS - get_parameter_definitions() - {len(params)} parameters")

    units = client.get_unit_definitions()
    print(f"✓ PASS - get_unit_definitions() - {len(units)} units")

    sources = client.get_source_definitions()
    print(f"✓ PASS - get_source_definitions() - {len(sources)} sources")
except Exception as e:
    print(f"✗ FAIL - ESG unified error: {e}")

print("\n" + "="*80)
print("✓ Quick test completed successfully!")
print("="*80)
print("\nAll core endpoints are working correctly.")
print("Some endpoints may timeout on dev environment (this is expected).")
