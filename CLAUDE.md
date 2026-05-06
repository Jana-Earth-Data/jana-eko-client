# CLAUDE.md — jana-eko-client project conventions

> **Maintenance note:** Shared rules (git workflow, shell scripting, AWS auth, deploy policy, etc.) live in the parent `repos/CLAUDE.md` and are inherited automatically. This file contains only project-specific instructions. When updating, ask: "Does this apply to every repo, or just this project?" Shared rules go in `repos/CLAUDE.md`; project-specific rules go here.

## Data sourcing policy — never proxy upstream APIs to analysts (NON-NEGOTIABLE)

**We ONLY EVER serve our own API endpoints from our own database.** Period.

- **Never** call a third-party data provider's API at request time on behalf of an analyst.
- **Never** pass through, proxy, mirror, or forward responses from upstream APIs (Climate TRACE, EDGAR, OpenAQ, GLEIF, NOAA, NASA FIRMS, GCP, etc.) to analyst-facing endpoints.
- **Always** ingest upstream data into our PostgreSQL database via the standard ingestion pipeline (Celery tasks, S3 staging, models, materialized views), then serve from our own models.
- If an analyst-facing endpoint exists today that proxies upstream, **it is a bug**. File an issue, scope a proper ingestion, and remove the proxy.

**Why:**
- Analyst trust requires reproducibility. Upstream APIs change, rate-limit, go down, return different shapes per region, and silently re-version. We cannot give analysts a stable platform on top of moving sand.
- Our SLA is our SLA. We cannot promise availability or latency on requests that depend on a third party answering in real time.
- Provenance, auditability, and time-travel queries require the data to live in our system of record.
- Caching a proxy is not a substitute for ingestion — a stale cache hides upstream changes instead of recording them.

**The only acceptable upstream API calls are:**
1. **Ingestion jobs** (Celery tasks under `data_sources/<source>/tasks.py`) that pull data into our DB.
2. **Internal admin/ops tooling** that the analyst never touches.

If you find yourself writing a DRF view that calls `requests.get("https://api.<provider>.org/...")` or instantiates a `<Provider>Client()` inside a view method — **stop**. That is a violation of this rule. The fix is to ingest the data, not to cache the proxy harder.

