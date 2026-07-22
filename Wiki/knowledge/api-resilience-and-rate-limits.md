# API resilience & rate-limit patterns

**Summary**: Reusable patterns for integrating an external/quoted API robustly — retry with backoff, rate-limit compliance, pagination, and multi-endpoint failover. Distilled from the ExampleDataTool Polygon downloader and the a vendor API client.

**Sources**: `ExampleDataTool/download_massive_intraday.py`; `ExampleApiApp` (FikaAmazonAPI `RequestService`, `AWSSigV4Signer`). No secrets imported.

**Last updated**: 2026-06-18

---

## Retry with backoff + honor `Retry-After`
Retry transient failures (HTTP 429, 5xx, network) with exponential backoff; if the response carries a `Retry-After`, honor it instead of guessing. ExampleDataTool does this **stdlib-only** via `urllib` — no `requests`/`httpx` needed.

## Rate-limit compliance as a first-class concern
Gate calls to the provider's quota. Two seen approaches: a **fixed-window limiter** (e.g. 5 calls/min via monotonic-time bucketing, sequential, no threading — ExampleDataTool) and **per-endpoint** tracking from response headers (`x-amzn-RateLimit-Limit`, sleep ≈ 1/rate — a vendor API). Treat the SLA as part of the contract, not an afterthought.

## Pagination via continuation token / `next_url`
Follow the provider's `next_url`/cursor; keep continuation stateless and idempotent (dedup by key/timestamp) so a failed run can resume. Gotcha: re-attach the API key to continuation URLs if the provider drops it.

## Multi-endpoint failover
If the primary endpoint fails, fall back to a secondary transparently (ExampleDataTool: Polygon → ExampleDataToole.com), logging the switch — simple redundancy without async complexity.

## Wrap behind a small internal interface
Keep auth + signing + retry behind one client/interface so upstream changes are contained and secrets stay out of business code (cf. the `IAmazonCredential` abstraction in ExampleApiApp).

## Related pages

- [[role-api-integrator]]
- [[package-local-mcp-server-as-mcpb]]
- [[no-secrets-or-private-account-data]]
