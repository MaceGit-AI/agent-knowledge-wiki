# Token-frugal tool / MCP output design

**Summary**: Design the output of any tool an LLM calls (MCP tool, CLI, subagent return) to be **compact by default**, so each call adds little to the agent's context. Tool results are re-read every subsequent turn — verbose output silently burns tokens.

**Type**: experience / pattern
**Stacks**: any (MCP servers, CLIs, agent tools)
**Provenance**: observed in a TradingView MCP bridge (a full "analyze my chart" flow is ~5–10KB instead of ~80KB); aligns with our [[local-recall-engine]] (returns snippets/references, not dumps) and Anthropic's "return lightweight references" guidance.
**Confidence**: medium
**Last updated**: 2026-06-19

---

## When it applies

Building anything an LLM calls — an MCP server, a CLI an agent pipes, a subagent's return value. Whatever the tool returns lands verbatim in context and is paid for again on every following turn.

## The techniques

- **Summary mode by default** — stats + the last N items, not the full series (e.g. OHLCV summary vs 100 bars); full data only on request.
- **Deduplicate** — collapse repeats to distinct values (price levels, zones) instead of every object.
- **Cap** long lists (e.g. ≤50) and note that more exist.
- **Pre-format for the reader** — row strings, not cell metadata/IDs/colors.
- **Filter to target** — a `filter` param so the caller fetches one thing, not everything.
- **Opt-in verbose** — `verbose: true` returns the raw/full payload only when actually needed.
- **Drop noise** — strip encoded blobs, internal IDs, and colors the agent won't use.

## Why

The working set the model re-reads each turn stays small → faster, cheaper, more room to reason. Same principle as our recall design (retrieve references, read only what's relevant) — see [[karpathy-loop-and-agent-discipline]].

## Related pages

- [[package-local-mcp-server-as-mcpb]]
- [[local-recall-engine]]
