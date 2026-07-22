# Config in AppData with a user-owned local override

**Summary**: Ship a default config template in the repo, copy it to a per-user location at first run, and let an optional `*.local.*` file override it. Keeps user settings out of version control and survives updates.

**Type**: experience / pattern

**Stacks**: any, dotnet

**Provenance**: ExampleApp (`TradingApp.IBClientApp`) @ project_instructions.yaml + PostBuild copy step.

**Confidence**: medium

**Last updated**: 2026-06-18

---

## Context

A desktop app needs settings that differ per machine/user (ports, tokens, sizes) without baking secrets into the repo or losing user edits on every build/update.

## Insight / Recipe

- Keep a template (`config.yaml`) in the repo; a PostBuild/first-run step copies it to the per-user dir (`%APPDATA%/<App>/` on Windows).
- Load order: defaults → `config.yaml` → **`config.local.yaml` wins**. The `.local` file is user-owned and git-ignored.
- Route all path resolution through one path service — never hardcode absolute paths.
- Generalizes to any stack (dotenv `.env.local`, `appsettings.Local.json`, etc.).

## Evidence

ExampleApp persists config in `%APPDATA%/TradingApp.IBClientApp/config.yaml` with an optional `config.local.yaml` override; the build copies the template on PostBuild.

## Related pages

