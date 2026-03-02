# Dependencies Documentation

This document outlines all dependencies for the jana-eko-client library and provides migration guidance for existing code.

## External Dependencies

### Required Dependencies

These are automatically installed when you `pip install jana-eko-client`:

| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | >= 0.24.0 | Async/sync HTTP client for API requests |
| `pydantic` | >= 2.0.0 | Data validation and type-safe models |
| `typing-extensions` | >= 4.5.0 | Backport of typing features for older Python versions |

### Development Dependencies

Optional dependencies for development work:

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >= 7.0.0 | Testing framework |
| `pytest-asyncio` | >= 0.21.0 | Async test support |
| `black` | >= 23.0.0 | Code formatting |
| `mypy` | >= 1.0.0 | Static type checking |
| `ruff` | >= 0.1.0 | Fast Python linter |

Install development dependencies:
```bash
pip install jana-eko-client[dev]
```

## Python Version Compatibility

- **Minimum**: Python 3.8
- **Tested**: Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Recommended**: Python 3.10+

## Jana Platform Dependencies

### Files that Currently Import `eko_client`

The following files in the Jana-refactor repository currently import or reference `eko_client`:

#### 1. `scripts/ingestion/setup_missing_countries_ingestion.py`

**Current Code:**
```python
# Add eko-client to path
sys.path.insert(0, str(eko_client_dir))
from eko_client import EkoUserClient
```

**Migration Path:**
After jana-eko-client is published to PyPI or installed from GitHub:

```python
# Simply import - no path manipulation needed
from eko_client import EkoUserClient
```

**Location**: `/Users/willardmechem/Projects/repos/Jana-refactor/scripts/ingestion/setup_missing_countries_ingestion.py`

#### 2. API Compatibility Comments

The following files contain comments referencing eko-client compatibility:

- **`fr-data-service/src/apps/data_sources/climatetrace/views.py`**
  - Line: `# Accept both 'sector' (ForeignKey) and 'sector_id' (for eko-client compatibility)`
  - Action: No changes needed - these comments document API design decisions

- **`fr-data-service/src/apps/data_sources/openaq/views.py`**
  - Line: `# The eko-client sends country_codes as a comma-separated string`
  - Line: `# Handle location_id parameter (for eko-client compatibility)`
  - Line: `# Django FilterSet uses location__id, but eko-client sends location_id`
  - Action: No changes needed - these document API parameter handling

- **`fr-data-service/src/apps/authentication/views.py`**
  - Line: `Used by eko-client get_user_info().`
  - Action: No changes needed - documents endpoint usage

## Installation Guide

### For Development (Editable Install)

```bash
# Clone the repository
git clone https://github.com/Jana-Earth-Data/jana-eko-client
cd jana-eko-client

# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e .[dev]
```

### From GitHub (Production)

```bash
# Install from main branch
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git

# Install from specific branch
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git@development

# Install specific version tag
pip install git+https://github.com/Jana-Earth-Data/jana-eko-client.git@v0.2.0
```

### From PyPI (Future)

```bash
pip install jana-eko-client
```

## Migration Timeline

### Phase 1: Setup (Current)
- ✅ Extract code to standalone repository
- ✅ Update package metadata (name, version, organization)
- ✅ Create comprehensive documentation
- ✅ Identify all dependencies

### Phase 2: Testing (Next Step)
- Test the library as a pip-installable package
- Update `scripts/ingestion/setup_missing_countries_ingestion.py` to use installed package
- Run integration tests with Jana API
- Verify all endpoints work correctly

### Phase 3: Deployment (After Testing)
- Publish to PyPI (or configure private package repository)
- Update all Jana repositories to use `pip install jana-eko-client`
- Remove old eko-client-python directory from Jana-refactor
- Update CI/CD pipelines

### Phase 4: Cleanup (Final)
- Run the removal script: `bash remove_eko_client_from_jana.sh`
- Commit changes to Jana-refactor repository
- Archive old code references

## Integration with Jana Platform

### Current Integration Points

1. **Script Usage**: `scripts/ingestion/setup_missing_countries_ingestion.py`
   - Uses `EkoUserClient` for API communication
   - After migration: Install jana-eko-client as dependency

2. **API Compatibility**: Views maintain backward compatibility
   - Parameter names accepted by API (e.g., `location_id`, `sector_id`)
   - Comment references document design decisions
   - No code changes needed

3. **Authentication**: Token-based auth via Jana API
   - `EkoUserClient` authenticates with username/password or token
   - `EkoAdminClient` requires admin privileges
   - Authentication flow remains unchanged

### Testing Checklist

Before removing old eko-client-python code:

- [ ] Install jana-eko-client from GitHub
- [ ] Test `scripts/ingestion/setup_missing_countries_ingestion.py` with new package
- [ ] Verify all API endpoints work (data, correlations, exports)
- [ ] Test async methods in production-like environment
- [ ] Confirm authentication works (both user and admin clients)
- [ ] Run integration tests against staging API
- [ ] Update requirements.txt in Jana-refactor if needed

## Breaking Changes

### None (v0.1.0 → v0.2.0)

The migration from `eko-client` to `jana-eko-client` is 100% backward compatible:

- ✅ Module name unchanged: Still `from eko_client import ...`
- ✅ Class names unchanged: Still `EkoUserClient`, `EkoAdminClient`
- ✅ Method signatures unchanged: All parameters remain the same
- ✅ Response formats unchanged: API responses identical

**Only change required**: Update package name in `pip install` commands

## Support and Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'eko_client'`
**Solution**: Ensure jana-eko-client is installed: `pip install jana-eko-client`

**Issue**: Import error after updating package
**Solution**: Reinstall with `pip install --force-reinstall jana-eko-client`

**Issue**: Version conflicts with existing eko-client
**Solution**: Uninstall old package first: `pip uninstall eko-client`, then install new package

### Getting Help

- **GitHub Issues**: https://github.com/Jana-Earth-Data/jana-eko-client/issues
- **Email**: contact@jana.earth
- **Documentation**: https://docs.jana.earth

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.2.0 | 2026-03-02 | Repository extraction, rename to jana-eko-client |
| 0.1.0 | 2026-02-28 | Sync/async wrapper refactor, exception handling improvements |
| 0.0.x | 2025-2026 | Initial development and feature additions |

## Future Enhancements

Planned improvements for future versions:

1. **Rate Limiting**: Built-in request throttling
2. **Caching**: Optional response caching for improved performance
3. **Retry Logic**: Configurable retry strategies
4. **Batch Operations**: Bulk request support
5. **Webhook Support**: Real-time notifications
6. **GraphQL Support**: Alternative query interface

---

**Last Updated**: 2026-03-02
**Maintainer**: Jana Earth Data Team
