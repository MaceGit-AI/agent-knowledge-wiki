# Package a local stdio MCP server as an .mcpb bundle

**Summary**: Local (stdio) MCP servers cannot be added through the Connectors dialog — that dialog is for remote/URL servers. Register them via config file, or package them as a self-contained `.mcpb` bundle for one-click install.

**Type**: experience / environment

**Stacks**: mcp, node

**Provenance**: example-electron-mcp (local clone) @ 2026-06-18, verified via `npx @anthropic-ai/mcpb validate` (schema passes) + `pack` producing a 3.3MB bundle.

**Confidence**: high

**Last updated**: 2026-06-18

---

## Context

A locally-cloned MCP server (`command: node …/server.js`) doesn't appear in the Connectors UI, and the user wonders why "it can't be installed like a connector".

## Insight / Recipe

- The **Connectors dialog only takes remote servers** (HTTP/SSE URL + OAuth) or packaged extensions. A local stdio server runs a program on the machine — by design it is registered via a config file, not a UI.
- Two valid paths:
  1. **Config**: add to project `.mcp.json` or `~/.claude.json` `mcpServers` → restart the client (MCP servers load at startup).
  2. **Bundle (`.mcpb`)**: add a `manifest.json` (`manifest_version`, `name`, `version`, `server.{type:node, entry_point, mcp_config:{command,args:["${__dirname}/src/server.js"]}}`), include `node_modules` so it is self-contained, add a `.mcpbignore` (drop `.git`, tests), then `npx @anthropic-ai/mcpb validate manifest.json` and `npx @anthropic-ai/mcpb pack .`. The host extracts the bundle and resolves `${__dirname}` at install time.
- Don't register the same server twice (config **and** bundle) or it runs twice.

## Evidence

`mcpb validate` passed and `pack` produced `example-electron-mcp.mcpb` (2163 files, node_modules bundled) this session.

## Related pages

- [[cdp-debug-electron-desktop-apps]]
