#!/bin/bash
#
# Remove eko-client-python from Jana-refactor Repository
#
# ⚠️  WARNING: Run this script ONLY after thoroughly testing jana-eko-client
# ⚠️  This script will permanently delete the eko-client-python directory
#
# Prerequisites:
# 1. jana-eko-client is installed and working (pip install jana-eko-client)
# 2. All scripts using eko_client have been updated
# 3. Integration tests have passed
# 4. You have committed all other changes
#
# Usage:
#   cd /path/to/jana-refactor
#   bash /path/to/jana-eko-client/remove_eko_client_from_jana.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}  Remove eko-client-python from Jana-refactor${NC}"
echo -e "${BLUE}=================================================${NC}"
echo

# Determine the Jana-refactor path
JANA_REFACTOR_PATH="${JANA_REFACTOR_PATH:-/Users/willardmechem/Projects/repos/Jana-refactor}"

if [ ! -d "$JANA_REFACTOR_PATH" ]; then
    echo -e "${RED}ERROR: Jana-refactor directory not found at: $JANA_REFACTOR_PATH${NC}"
    echo -e "${YELLOW}Set JANA_REFACTOR_PATH environment variable to the correct path${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found Jana-refactor at: $JANA_REFACTOR_PATH${NC}"
echo

# Check if eko-client-python directory exists
EKO_CLIENT_DIR="$JANA_REFACTOR_PATH/eko-client-python"

if [ ! -d "$EKO_CLIENT_DIR" ]; then
    echo -e "${YELLOW}ℹ  eko-client-python directory not found. Already removed?${NC}"
    exit 0
fi

echo -e "${YELLOW}⚠️  WARNING: This will permanently delete the following:${NC}"
echo -e "   ${RED}$EKO_CLIENT_DIR${NC}"
echo
echo -e "${YELLOW}This action cannot be undone!${NC}"
echo
read -p "Have you verified that jana-eko-client is working? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}Aborted. Please test jana-eko-client thoroughly before running this script.${NC}"
    exit 1
fi

echo
read -p "Are you ABSOLUTELY SURE you want to proceed? (yes/no): " FINAL_CONFIRM

if [ "$FINAL_CONFIRM" != "yes" ]; then
    echo -e "${RED}Aborted.${NC}"
    exit 1
fi

echo
echo -e "${BLUE}Starting removal process...${NC}"
echo

# Step 1: Update setup_missing_countries_ingestion.py
echo -e "${BLUE}[1/5] Updating setup_missing_countries_ingestion.py...${NC}"

SCRIPT_PATH="$JANA_REFACTOR_PATH/scripts/ingestion/setup_missing_countries_ingestion.py"

if [ -f "$SCRIPT_PATH" ]; then
    # Create backup
    cp "$SCRIPT_PATH" "$SCRIPT_PATH.backup"
    echo -e "${GREEN}   ✓ Created backup: $SCRIPT_PATH.backup${NC}"

    # Update the script to use installed package
    cat > "$SCRIPT_PATH" << 'EOFPYTHON'
#!/usr/bin/env python3
"""
Setup OpenAQ S3 bulk ingestion for missing countries.

This script:
1. Identifies countries with locations but no measurements
2. Gets location IDs for those countries
3. Creates an ingestion job via the unified API
4. Triggers the job execution
"""

import sys
import os
from pathlib import Path

# Import jana-eko-client (installed via pip install jana-eko-client)
from eko_client import EkoUserClient
import json

# Configuration
BASE_URL = os.getenv("EKO_API_URL", "http://localhost:8000")
USERNAME = os.getenv("EKO_USERNAME", "wmechem")
PASSWORD = os.getenv("EKO_PASSWORD", "Sani2025!")

def main():
    print("=" * 80)
    print("OpenAQ Missing Countries Ingestion Setup")
    print("=" * 80)
    print()

    # Initialize client
    client = EkoUserClient(
        base_url=BASE_URL,
        username=USERNAME,
        password=PASSWORD,
        timeout=60
    )

    # Step 1: Get country totals to identify missing countries
    print("📊 Step 1: Analyzing current data coverage...")
    print("-" * 80)

    try:
        country_totals = client.get_openaq_measurements_country_totals()
        countries_with_data = {item['country_code'] for item in country_totals}
        print(f"✅ Countries with measurement data: {len(countries_with_data)}")
        print(f"   {', '.join(sorted(countries_with_data))}")
    except Exception as e:
        print(f"⚠️  Error getting country totals: {e}")
        countries_with_data = set()

    # Step 2: Get all locations to find countries without data
    print()
    print("📋 Step 2: Getting all locations...")
    print("-" * 80)

    try:
        # Get locations (paginated)
        all_locations = []
        offset = 0
        limit = 10000

        while True:
            response = client.get_openaq_locations(limit=limit, offset=offset)
            locations = response.get('results', [])
            if not locations:
                break

            all_locations.extend(locations)
            offset += len(locations)

            if len(locations) < limit:
                break

            if offset % 50000 == 0:
                print(f"   Fetched {offset:,} locations...")

        print(f"✅ Total locations: {len(all_locations):,}")

        # Group by country
        locations_by_country = {}
        for loc in all_locations:
            country = loc.get('country_code')
            if country:
                if country not in locations_by_country:
                    locations_by_country[country] = []
                locations_by_country[country].append(loc)

        print(f"✅ Countries with locations: {len(locations_by_country)}")

        # Find missing countries
        missing_countries = set(locations_by_country.keys()) - countries_with_data

        print()
        print("=" * 80)
        print(f"📊 Analysis Results:")
        print("=" * 80)
        print(f"   Countries with locations: {len(locations_by_country)}")
        print(f"   Countries with measurements: {len(countries_with_data)}")
        print(f"   Countries missing measurements: {len(missing_countries)}")
        print()

        if not missing_countries:
            print("✅ All countries already have measurement data!")
            return

        print("❌ Countries missing measurement data:")
        missing_locations = {}
        total_location_ids = []

        for country_code in sorted(missing_countries):
            country_locs = locations_by_country[country_code]
            location_ids = [loc['openaq_id'] for loc in country_locs]
            missing_locations[country_code] = location_ids
            total_location_ids.extend(location_ids)
            print(f"   {country_code}: {len(location_ids):,} locations")

        print()
        print(f"📊 Total location IDs to ingest: {len(total_location_ids):,}")
        print()

    except Exception as e:
        print(f"❌ Error getting locations: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Create ingestion job
    print("=" * 80)
    print("🚀 Step 3: Creating ingestion job...")
    print("=" * 80)

    job_config = {
        "name": "OpenAQ S3 Bulk - Missing Countries",
        "description": f"Bulk ingest measurements for {len(missing_countries)} countries missing data ({len(total_location_ids):,} locations) via S3 bulk ingestion",
        "data_source": 1,  # OpenAQ data source ID
        "job_type": "incremental_openaq_s3_bulk",
        "configuration": {
            "batch_size": 10000,
            "location_ids": total_location_ids[:1000] if len(total_location_ids) > 1000 else total_location_ids  # Limit for initial test
        },
        "priority": "normal",
        "is_active": True,
        "max_retries": 3,
        "timeout_minutes": 1440  # 24 hours
    }

    print(f"   Job name: {job_config['name']}")
    print(f"   Job type: {job_config['job_type']}")
    print(f"   Location IDs: {len(job_config['configuration']['location_ids']):,}")
    print(f"   Batch size: {job_config['configuration']['batch_size']}")
    print()

    try:
        # Note: This would require the management API endpoint
        # For now, we'll print the configuration for manual creation
        print("⚠️  Note: Job creation via API requires management endpoints.")
        print("   Please create the job manually using the following configuration:")
        print()
        print(json.dumps(job_config, indent=2))
        print()
        print("=" * 80)
        print("📝 Next Steps:")
        print("=" * 80)
        print("1. Create job using the configuration above")
        print("2. Trigger the job execution")
        print("3. Monitor progress via execution logs")
        print("=" * 80)

        # Save configuration to file
        project_root = Path(__file__).parent.parent
        config_file = project_root / 'scripts' / 'missing_countries_job_config.json'
        with open(config_file, 'w') as f:
            json.dump(job_config, f, indent=2)

        print(f"✅ Configuration saved to: {config_file}")

    except Exception as e:
        print(f"❌ Error creating job: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
EOFPYTHON

    echo -e "${GREEN}   ✓ Updated script to use installed jana-eko-client package${NC}"
else
    echo -e "${YELLOW}   ℹ  Script not found: $SCRIPT_PATH${NC}"
fi

echo

# Step 2: Remove eko-client-python directory
echo -e "${BLUE}[2/5] Removing eko-client-python directory...${NC}"

rm -rf "$EKO_CLIENT_DIR"
echo -e "${GREEN}   ✓ Deleted: $EKO_CLIENT_DIR${NC}"
echo

# Step 3: Check for any remaining references
echo -e "${BLUE}[3/5] Checking for remaining references to eko-client...${NC}"

cd "$JANA_REFACTOR_PATH"

# Search for sys.path.insert references (excluding the script we just updated)
echo -e "${YELLOW}   Searching for sys.path references to eko-client...${NC}"
SYSPATH_REFS=$(grep -r "sys.path.insert.*eko-client" --include="*.py" . 2>/dev/null | grep -v "setup_missing_countries_ingestion.py.backup" || true)

if [ ! -z "$SYSPATH_REFS" ]; then
    echo -e "${YELLOW}   ⚠️  Found sys.path references:${NC}"
    echo "$SYSPATH_REFS"
    echo
else
    echo -e "${GREEN}   ✓ No sys.path references found${NC}"
fi

# Search for import references (these are OK - just showing for info)
echo -e "${YELLOW}   Listing files that import eko_client (should use pip-installed package):${NC}"
IMPORT_REFS=$(grep -r "from eko_client import\|import eko_client" --include="*.py" . 2>/dev/null | grep -v ".backup" | head -5 || true)

if [ ! -z "$IMPORT_REFS" ]; then
    echo "$IMPORT_REFS"
    echo -e "${GREEN}   ✓ These are OK - they'll use the pip-installed package${NC}"
else
    echo -e "${GREEN}   ✓ No import references found${NC}"
fi

echo

# Step 4: Create commit
echo -e "${BLUE}[4/5] Preparing git commit...${NC}"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}   ERROR: Not a git repository${NC}"
    echo -e "${YELLOW}   Please navigate to the Jana-refactor repository root${NC}"
    exit 1
fi

# Stage changes
git add scripts/ingestion/setup_missing_countries_ingestion.py 2>/dev/null || true
git add -u . 2>/dev/null || true  # Stage deletions

echo -e "${GREEN}   ✓ Staged changes${NC}"
echo

# Step 5: Show summary
echo -e "${BLUE}[5/5] Summary${NC}"
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}✓ eko-client-python directory removed${NC}"
echo -e "${GREEN}✓ Scripts updated to use jana-eko-client${NC}"
echo -e "${GREEN}✓ Changes staged for commit${NC}"
echo -e "${GREEN}=================================================${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Review changes: ${BLUE}git status${NC}"
echo -e "  2. Review diff: ${BLUE}git diff --cached${NC}"
echo -e "  3. Commit changes: ${BLUE}git commit -m \"Remove eko-client-python, use jana-eko-client package\"${NC}"
echo -e "  4. Test thoroughly before pushing!"
echo
echo -e "${YELLOW}To install jana-eko-client:${NC}"
echo -e "  ${BLUE}pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git${NC}"
echo
echo -e "${GREEN}Done!${NC}"
