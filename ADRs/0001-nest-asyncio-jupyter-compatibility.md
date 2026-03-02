# ADR-0001: Automatic nest_asyncio Support for Jupyter Compatibility

**Date:** 2026-03-02
**Status:** Accepted
**Deciders:** Jana Earth Data Engineering Team
**Supersedes:** N/A
**Superseded by:** N/A

## Context

The jana-eko-client library provides both async (`*_async()`) and synchronous wrapper methods for all API operations. The sync wrappers use `asyncio.run_until_complete()` with a persistent event loop to enable multiple sequential calls while maintaining proper HTTP connection pooling.

However, Jupyter notebooks run their own event loop in the background. When sync wrapper methods try to use `run_until_complete()` on a persistent loop, it conflicts with Jupyter's running loop, causing errors:

```
RuntimeError: Cannot run the event loop while another loop is running
```

This creates a poor user experience for data scientists and analysts who want to use the client library in Jupyter notebooks - a common use case for environmental data analysis.

Technical forces at play:
- **Jupyter's event loop**: Always running, cannot be stopped or replaced
- **Our persistent loop approach**: Works perfectly in scripts, conflicts in Jupyter
- **User expectations**: Same code should work in both scripts and notebooks
- **Connection pooling**: Must maintain persistent connections for performance

## Decision Drivers

- **Developer experience**: Library should "just work" in Jupyter without special configuration
- **Performance**: Must maintain persistent HTTP connections (not create new client per call)
- **Zero user configuration**: No manual setup, import statements, or environment detection needed
- **Backward compatibility**: Must not break existing script-based usage
- **Minimal dependencies**: Additional dependencies should be lightweight and well-maintained

## Considered Options

### Option 1: Document "Use async methods only in Jupyter"

**Description:** Update documentation to recommend using `*_async()` methods with `await` in Jupyter, sync methods in scripts.

**Pros:**
- No code changes required
- No additional dependencies
- Jupyter natively supports `await` in cells

**Cons:**
- Requires users to understand async/sync differences
- Different code patterns for different environments (poor DX)
- Users must remember which environment they're in
- Breaks the "just works" principle

### Option 2: Require users to import and apply nest_asyncio

**Description:** Document that users must install and apply `nest_asyncio` manually in Jupyter:
```python
import nest_asyncio
nest_asyncio.apply()
```

**Pros:**
- Small code change (just documentation)
- Users have control over when it's applied

**Cons:**
- Extra boilerplate in every notebook
- Users must remember to install nest_asyncio
- Poor developer experience
- Common source of support questions

### Option 3: Automatic environment detection with nest_asyncio (CHOSEN)

**Description:** Sync wrapper automatically detects whether an event loop is running (Jupyter) and applies `nest_asyncio` transparently. Falls back to persistent loop approach in scripts.

**Implementation:**
```python
def sync_wrapper(self, *args, **kwargs):
    try:
        # Running in Jupyter/async environment
        loop = asyncio.get_running_loop()

        # Apply nest_asyncio for compatibility
        import nest_asyncio
        nest_asyncio.apply()

        return loop.run_until_complete(async_method(self, *args, **kwargs))

    except RuntimeError:
        # No running loop - regular script
        if not hasattr(self, '_sync_loop'):
            self._sync_loop = asyncio.new_event_loop()

        return self._sync_loop.run_until_complete(
            async_method(self, *args, **kwargs)
        )
```

**Pros:**
- Zero user configuration - "just works" everywhere
- Same code works in Jupyter and scripts
- Maintains persistent connections in both environments
- Excellent developer experience
- Minimal dependency (`nest_asyncio` is 3KB, pure Python, no dependencies)

**Cons:**
- Adds one dependency (nest_asyncio)
- Slightly more complex sync wrapper logic
- `nest_asyncio.apply()` is global (but idempotent and safe)

## Decision

We will implement **Option 3: Automatic environment detection with nest_asyncio**.

The sync wrapper will automatically detect whether it's running in an environment with an active event loop (Jupyter, IPython, async frameworks) and transparently handle it using `nest_asyncio`. In traditional Python scripts, it will use the existing persistent event loop approach.

This decision prioritizes developer experience and the "just works" principle. The jana-eko-client library is designed for data scientists, researchers, and developers who may not be async experts. They should be able to write the same simple code everywhere:

```python
from eko_client import EkoUserClient

client = EkoUserClient(...)
health = client.get_health()  # Works in Jupyter AND scripts
params = client.get_openaq_parameters()
```

The `nest_asyncio` library is:
- **Tiny**: 3KB, single file, no dependencies
- **Stable**: Maintained since 2018, widely used in Jupyter ecosystem
- **Safe**: Idempotent, applying multiple times has no effect
- **Well-tested**: Used by IPython, Jupyter, and many async libraries

## Consequences

### Positive

- **Seamless Jupyter support**: Sync methods now work in Jupyter notebooks without any user configuration
- **Consistent API**: Same code works everywhere - scripts, notebooks, REPL, async frameworks
- **Better DX**: Users don't need to understand async/sync differences or event loop mechanics
- **Fewer support questions**: "Why doesn't it work in Jupyter?" questions eliminated
- **Wider adoption**: Data scientists can use the library immediately in their preferred environment

### Negative

- **Additional dependency**: Adds `nest_asyncio` to dependencies (though it's tiny and stable)
- **Global modification**: `nest_asyncio.apply()` modifies the global event loop policy (but this is safe and expected in Jupyter)
- **Slightly more complex wrapper**: Sync wrapper has two code paths (though well-tested)

### Neutral

- **Dependency management**: Must ensure `nest_asyncio` is included in `pyproject.toml` dependencies
- **Testing**: Should test both code paths (Jupyter environment and script environment)
- **Documentation**: Should document that this works automatically (users don't need to know the details)
- **Performance**: Negligible impact - environment detection is a simple try/except, runs once per call

## Implementation Notes

1. Add `nest_asyncio>=1.5.0` to `pyproject.toml` dependencies
2. Modify `eko_client/sync_wrapper.py` `_create_sync_wrapper()` function
3. Import `nest_asyncio` inside the wrapper (lazy import to avoid import cost for async-only users)
4. Apply `nest_asyncio.apply()` only when a running loop is detected
5. Update tests to verify both code paths
6. Update README to mention Jupyter support (but users don't need to do anything special)

## References

- [nest_asyncio GitHub](https://github.com/erdewit/nest_asyncio)
- [Jupyter event loop discussion](https://ipython.readthedocs.io/en/stable/interactive/autoawait.html)
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- Related: Sync wrapper fix for multiple sequential calls (commit b668fe0)
