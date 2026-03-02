# Designing an Invisible Async Query Architecture for Massive Postgres Workloads

**Generated on:** 2026-02-12 06:21:58 UTC

------------------------------------------------------------------------

## 1. Problem Overview

You have:

-   A **PostgreSQL database** connected to a **Django API server**
-   \~20 climate data tables
-   One table with **1+ billion rows**, potentially growing 10x
-   A **Python client library** that wraps the API
-   Users running analytics from **Jupyter notebooks**

### Current Behavior

The Python client:

1.  Sends an HTTP request to the Django API
2.  Waits for the response synchronously
3.  Returns results to the user

This works for small queries, but breaks down for:

-   Long-running queries (minutes to hours)
-   Large result sets (GB-scale responses)
-   Expensive joins or full-table scans

------------------------------------------------------------------------

## 2. Goal

Provide a solution that:

-   Supports long-running queries
-   Does not require users to manually poll job queues
-   Hides job IDs from users
-   Feels natural in Jupyter notebooks
-   Scales to billion+ row datasets

------------------------------------------------------------------------

## 3. Recommended Architecture

The best practice approach is:

> Sync-if-fast, Async-if-slow + QueryResult handle abstraction

------------------------------------------------------------------------

## 4. Server-Side Design

### 4.1 Endpoint Behavior

`POST /query`

Server logic:

-   If query is fast → return `200 OK` with results
-   If query is long-running → return `202 Accepted` with:
    -   `job_id`
    -   `status_url`
    -   optional ETA or progress metadata

Example 202 response:

``` json
{
  "job_id": "abc123",
  "status_url": "/jobs/abc123"
}
```

------------------------------------------------------------------------

### 4.2 Job Status Endpoint

`GET /jobs/{job_id}`

Returns:

``` json
{
  "status": "running",
  "progress": 0.63
}
```

When complete:

``` json
{
  "status": "completed",
  "download_url": "https://object-storage/result.parquet",
  "format": "parquet",
  "row_count": 245000000
}
```

------------------------------------------------------------------------

### 4.3 Result Storage Strategy

Do NOT return large datasets over JSON.

Instead:

-   Materialize results to:
    -   Parquet (preferred)
    -   CSV (fallback)
-   Store in object storage (e.g., S3-compatible)
-   Return pre-signed download URL

Benefits:

-   Efficient columnar format
-   Streamable
-   Scales to very large results
-   Compatible with Pandas, Polars, PyArrow

------------------------------------------------------------------------

## 5. Client-Side Design

### 5.1 Introduce a QueryResult Abstraction

Instead of returning raw data, return:

``` python
res = client.query(...)
```

This returns a `QueryResult` object.

------------------------------------------------------------------------

### 5.2 User Experience Options

#### Option A: Implicit Blocking

``` python
df = res.to_pandas()
```

If async job: - Client polls in background - Blocks only when
`.to_pandas()` is called

------------------------------------------------------------------------

#### Option B: Explicit Wait

``` python
res.wait()
df = res.to_pandas()
```

------------------------------------------------------------------------

#### Option C: Async Native

``` python
df = await res
```

------------------------------------------------------------------------

## 6. QueryResult API Design

Recommended methods:

``` python
res.wait(timeout=None)
res.to_pandas()
res.to_polars()
res.iter_batches(batch_size=100_000)
res.download(path="result.parquet")
res.cancel()
res.status
res.progress
```

### Optional Features

-   Exponential backoff polling
-   Jupyter-friendly status display (`__repr__` override)
-   Local result caching
-   Retry logic for transient failures

------------------------------------------------------------------------

## 7. Polling Implementation Strategy

When API returns `202`:

-   Create background polling thread or asyncio task
-   Periodically call `/jobs/{id}`
-   Update status internally
-   When completed:
    -   Fetch download_url
    -   Stream result

Users never see job IDs.

------------------------------------------------------------------------

## 8. Determining Long-Running Queries

Possible strategies:

### 8.1 Planner-Based

Use:

``` sql
EXPLAIN (FORMAT JSON)
```

Estimate:

-   Total cost
-   Expected rows
-   Join complexity

Route to async if above threshold.

------------------------------------------------------------------------

### 8.2 Rule-Based

Examples:

-   Query touches billion-row table without time filter
-   Query requests wide date range
-   Query contains heavy joins

------------------------------------------------------------------------

### 8.3 Resource-Based

-   If concurrency high → force async
-   If system under load → queue job

------------------------------------------------------------------------

## 9. Handling Large Results

Large result sets require:

-   Streaming Parquet
-   Arrow batch iteration
-   Avoid loading entire dataset into memory

Example:

``` python
for batch in res.iter_batches(batch_size=100_000):
    process(batch)
```

------------------------------------------------------------------------

## 10. Minimal Migration Path

If redesigning API is expensive:

Add only:

1.  `POST /query`
2.  `GET /jobs/{id}`
3.  `POST /jobs/{id}/cancel`

Implement `QueryResult` wrapper in client.

------------------------------------------------------------------------

## 11. Why This Works

This architecture:

-   Encapsulates async complexity
-   Scales to billions of rows
-   Works naturally in Jupyter
-   Maintains simple API surface
-   Prevents JSON overloading
-   Enables future streaming improvements

------------------------------------------------------------------------

## 12. Final Recommendation

For a massive climate dataset (1B+ rows):

**Use:**

-   Async job execution
-   Parquet materialization
-   Object storage for results
-   QueryResult abstraction in Python client
-   Auto polling hidden from user

This approach provides the cleanest UX while maintaining
enterprise-grade scalability.

------------------------------------------------------------------------

# End of Document
