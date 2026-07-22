# Drive an Electron/Chromium desktop app via CDP

**Summary**: Any Chromium/Electron desktop app can be inspected and automated locally through the Chrome DevTools Protocol by launching it with `--remote-debugging-port`, then talking to `http://localhost:<port>`.

**Type**: experience / environment

**Stacks**: electron, chromium, cdp, mcp

**Provenance**: example-electron-mcp (local clone) @ 2026-06-18, verified via `curl http://localhost:9222/json/version` and `node src/cli/index.js status` returning live chart data.

**Confidence**: high

**Last updated**: 2026-06-18

---

## Context

You want an agent or script to read/observe a running desktop app (TradingView Desktop, VS Code, Slack, Discord — all Electron). No public API, but it is Chromium under the hood.

## Insight / Recipe

1. Launch the app with the standard Chromium flag `--remote-debugging-port=9222`. For Store/packaged apps that are not directly executable, launch via the shell app id with the flag appended (a small launcher/batch wrapper is the reliable way).
2. Confirm CDP is up: `curl http://localhost:9222/json/version` → returns Browser/WebKit/`webSocketDebuggerUrl`. `…/json` lists the targets (tabs).
3. Drive it via any CDP client (`chrome-remote-interface`, Playwright-over-CDP, a custom bridge).
4. The debug port is **off by default** and must be explicitly enabled — nothing is exposed without that deliberate flag.

## Evidence

In this session the TradingView Desktop bridge returned live state (`chart_symbol`, real-time quote) over CDP on port 9222 immediately after the flagged launch; `status` reported `cdp_connected: true`.

## Related pages

- [[package-local-mcp-server-as-mcpb]]
