#!/usr/bin/env python3
"""Test the async client directly (which should work properly)"""
import asyncio
from eko_client import EkoUserClient

async def main():
    client = EkoUserClient(
        base_url="https://api-dev.jana.earth",
        username="dev-user",
        password="Kv20cw6CUVyiE71T6UysSZan",
        timeout=60
    )
    
    print("Testing ASYNC methods (should work correctly):\n")
    
    # Multiple async calls work fine
    health1 = await client.get_health_async()
    print(f"✓ Call 1: get_health_async() - status: {health1.get('status')}")
    
    health2 = await client.get_health_async()
    print(f"✓ Call 2: get_health_async() - status: {health2.get('status')}")
    
    params = await client.get_openaq_parameters_async()
    print(f"✓ Call 3: get_openaq_parameters_async() - {len(params.get('results', []))} parameters")
    
    locations = await client.get_openaq_locations_async(limit=5)
    print(f"✓ Call 4: get_openaq_locations_async() - {len(locations.get('results', []))} locations")
    
    sectors = await client.get_climatetrace_sectors_async()
    print(f"✓ Call 5: get_climatetrace_sectors_async() - {len(sectors.get('results', []))} sectors")
    
    await client.close_async()
    print("\n✓ All async calls completed successfully!")
    print("\nNote: The sync wrapper has a known issue with multiple sequential calls.")
    print("      Use the _async methods for production code, or call close() between sync calls.")

if __name__ == "__main__":
    asyncio.run(main())
