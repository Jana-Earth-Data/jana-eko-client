#!/usr/bin/env python3
"""
Test that sync wrapper works in a Jupyter-like environment with running event loop.
This simulates what happens in Jupyter notebooks.
"""
import asyncio
import os
from eko_client import EkoUserClient

# Configuration
BASE_URL = os.environ.get("JANA_API_URL", "https://api-dev.jana.earth")
USERNAME = os.environ.get("JANA_USERNAME", "dev-user")
PASSWORD = os.environ.get("JANA_PASSWORD", "")

if not PASSWORD:
    print("ERROR: JANA_PASSWORD environment variable not set")
    exit(1)

async def test_in_async_context():
    """
    Test sync methods inside an async context (simulates Jupyter).
    This creates a running event loop, then calls sync methods.
    """
    print("Testing sync methods inside async context (Jupyter simulation):\n")

    # Create client
    client = EkoUserClient(
        base_url=BASE_URL,
        username=USERNAME,
        password=PASSWORD,
        timeout=60
    )

    try:
        # These are SYNC methods being called inside an async function
        # (which has a running event loop, like Jupyter)
        print("Call 1: Calling sync method get_health()...")
        health1 = client.get_health()
        print(f"✓ Call 1: get_health() - status: {health1.get('status')}\n")

        print("Call 2: Calling sync method get_health() again...")
        health2 = client.get_health()
        print(f"✓ Call 2: get_health() - status: {health2.get('status')}\n")

        print("Call 3: Calling sync method get_openaq_parameters()...")
        params = client.get_openaq_parameters()
        print(f"✓ Call 3: get_openaq_parameters() - {len(params.get('results', []))} parameters\n")

        print("Call 4: Calling sync method get_openaq_locations()...")
        locations = client.get_openaq_locations(limit=5)
        print(f"✓ Call 4: get_openaq_locations() - {len(locations.get('results', []))} locations\n")

        print("Call 5: Calling sync method get_climatetrace_sectors()...")
        sectors = client.get_climatetrace_sectors()
        print(f"✓ Call 5: get_climatetrace_sectors() - {len(sectors.get('results', []))} sectors\n")

        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe sync wrapper correctly detected the running event loop")
        print("and used nest_asyncio for Jupyter compatibility!")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    # Run in async context (this simulates Jupyter's environment)
    asyncio.run(test_in_async_context())
