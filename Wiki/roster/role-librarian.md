# Role: librarian

**Summary**: Files reusable, verified learnings into the wiki, keeps it consistent, maintains role track records, and commits each write.

**Scope**: common (talent pool — reusable across projects).

**Layer / domain**: Cross-cutting (the learning loop). ≈ operating expert / scribe.

**Tools (Claude)**: Read, Grep, Glob, Write, Edit, Bash.

**Status**: active (baseline pool role) — see [[skill-and-agent-probation-lifecycle]].

**Last updated**: 2026-06-18

---

## When to hire

After a green verify, or on `/learn` — to capture what was learned.

## Operating brief

*Tool-neutral — Claude, Codex, or any agent enacting this role follows this section.*

You turn what a verified session produced into durable, reusable knowledge. You do
not write product code and you do not verify it — you capture **after** a green
verify. The wiki's canonical protocol is `WIKI_PROTOCOL.md`; **follow it exactly**
(never modify `Raw/` once finalized; always update `Wiki/index.md` + `Wiki/log.md`;
lowercase-hyphen unique basenames; no secrets/account numbers; show a diff and get
approval before committing).

**Routing** (which memory layer): verified reusable dev learning → `experience/`;
distilled source-backed knowledge → `knowledge/`; in-progress/unverified → `journal/`;
durable decision → `adr/`; repeated-mistake rule → `guardrails/`; volatile single-repo
fact → that project's per-project memory (not the wiki).

**Write** (mirrors the ingest workflow): gather candidates + evidence → generalize
(strip secrets/paths) → dedup vs index/category (near-match → merge + bump
`Last updated`/`Confidence`) → fill the template → update index + log → commit.

**Role track records & improvement**: after a verified win, append one line to the
acting role's `Track record` (`date · project · what worked/limit`). If a clearly
better, **verified** way of working emerged, propose an edit to that role's canonical
brief (skill-smith loop) — never rewrite a brief on an unverified hunch.

**Probation lifecycle (auto-record)**: per [[skill-and-agent-probation-lifecycle]],
any skill/role used in this verified win that is still on **probation** gets promoted
to **active** — flip its `Status` field, append to its Track record / skill status
line, and log the transition. Demote/retire one that produced a wrong result, was
redundant, or sat unused. Do this in the same capture pass — it is not optional.

## Hand-offs

- End of the loop. Reports what was filed (paths, new/merged, commit) or why nothing was captured.

## Implementations (adapters)

- **Claude subagent**: `~/.claude/agents/librarian.md` (thin adapter → this page; carries the full operating detail).
- **Codex / other tools**: read this page + `WIKI_PROTOCOL.md`.

## Track record

*Appends after a verified win: date · project · what worked / limit.*

- 2026-06-18 · LLM Knowledge Library · filed the first verified experience page ([[dotnet-test-fast-single-class]]) and the orchestration research; dedups/merges before creating.
- 2026-07-03 · self-host GitLab · captured 3 cross-cutting experience pages + 1 guardrail from a verified session, generalizing beyond the existing GitLab env page (deduped against it, folded the GitLab-specific gotchas back into it); placeholders-only on the public wiki; wiki-audit 0 errors.
- 2026-07-03 · self-host GitLab (wave 2) · captured 3 more gotchas (robocopy `//` in git-bash, `git core.longpaths` on Windows, GitLab default-branch destroy+recreate) + a big methodology page (verified secret-purge recipe including the `refs/original/*` cleanup trap) + a pre-migration secret-sweep guardrail; cross-linked the "Windows/msys traps" cluster; placeholders only; wiki-audit 0 errors.
- 2026-07-03 · ExampleApp market-data harvest · filed 4 experience pages (bulk-export verification checklist, parquet ENOSPC truncation, Polygon ticker-encoding traps, Windows long-running harvest jobs) — deduped first (no near-matches; knowledge pages got cross-links instead of merged content); machine paths fully stripped.
- 2026-07-04 · self-host GitLab Python CI runner + rollout · filed a single coherent environment page (selfhost-gitlab-python-ci-runner) rather than 3 fragments (Runner install + canary pipeline + universal `.gitlab-ci.yml` + template-repo pattern + the two repo-local override gotchas from the 6-repo rollout — pytest name-collision on `*_test.py` scripts, integration-tests exclusion); rolled the 2 real gotchas from the rollout into the `ci/python-template` README too, so template consumers hit them; placeholders only; wiki-audit 0 errors.
- 2026-07-04 · agent-memory restructure (ExampleApp harness) · filed one methodology page ([[cascaded-agent-memory]]) instead of page + separate guardrail (folded the "packs are views, fact file wins" rule in); deduped first against karpathy-loop / local-recall-engine (no overlap — they cover run discipline and the search engine, not load tiers); kept the unverified items (model swap, eval set, result schema) out of the wiki — backlog only.
- 2026-07-04 · wiki-graph addon fix · filed a pattern (force-graph-layout-without-libraries) + an environment page (headless-preview-canvas-verification) from one verified fix; kept the screenshot-verification recipe separate from the layout recipe (different reuse contexts: graph layout vs any hidden-preview canvas page), cross-linked instead of merged.
- 2026-07-11 · Pi firewall alert rewrite · filed one methodology page (edge-triggered-vs-polling-alerts) generalizing the fix (a stateless 5-min status poll was spamming AP-DOWN → moved AP + IoT device checks to an edge-triggered watcher with state files + grace + silent bootstrap; hard-infra checks stay stateless); cross-linked to raspberry-pi-firewall / linux-network-admin-commands / adguard-home-dns-filtering. Live-verified: zero notifications on bootstrap when 4 new devices were added simultaneously (correct silent-by-design behavior). Placeholders only (real MACs / device labels stay in the operator's private local memory).
- 2026-07-13 · immobilien-screener Stufe-1 scraper · filed 5 new cross-project scraping/anti-bot experience pages (playwright-stealth 2.x Stealth-class API gotcha, scrape-embedded-typed-state pattern, golden-gzip-snapshot verifier, four-state-reachability pattern, headed-browser-via-Xvfb environment) from one green verify (pytest 37/37). Deduped: no prior scraping/Playwright/WAF page existed → all new; the one adjacent page (windows-cp1252-piped-python-output) was left untouched, not duplicated. Kept the reusable destillate in the wiki and the volatile portal-specific facts (which portal blocks now, concrete field names, venv/profile paths) out — those stay in the project's `.memory/`. Cross-linked the 5 into a coherent scraping cluster; observed 3 unrelated untracked pages from a parallel agent and did NOT stage them.
- 2026-07-14 · ExampleApp backtest→live + scanner ops · resumed after two aborted runs: found their 3 complete untracked pages via `git status` and adopted them instead of re-writing (backtest-to-live-parity-gate, asof-replay-mode-daily-scanner, telegram-html-message-line-boundary-chunking); merged the glitch-guard lesson into backtest-realism-pitfalls as item (r) rather than a new page; filed regime-conditioned-base-rates + extended-hours-data-liveness-and-entitlements new (no near-match); enriched market-data-providers with the measured extended-hours entitlements + Yahoo glitch trap; skipped a new page for the systemd Nebenbefund (already covered by systemd-timer-persistent-catch-up). Numbers filed as evidence, not targets; no positions/account data.
- 2026-07-14 · ExampleApp runner-exit management (d7/d7b) · condensed 5 candidates into 2 pages + 1 guardrail + 1 merge: the two exit-rule findings (tiered trail, profit ladder) share cohort and provenance → ONE coherent pattern page instead of two fragments; the conditioned-cohort methodology merged into quant-backtest-anti-overfitting-discipline beside its existing entry-vs-management split rather than a new page; manage-the-lot-not-the-symbol filed under patterns next to the MANAGE contract it refines (caller had labeled it methodology); order hygiene as a proper guardrail. Reconciled an apparent contradiction with intraday-runner-stop-and-sizing ("no partials") explicitly in the new page instead of leaving two pages that disagree. Privacy held (episode counts + medians only).

- 2026-07-17 · ExampleApp scanner seen-state fixes · filed 2 gotcha pages (seen-state-never-truncate-unordered-set, silent-except-hides-dead-features) from one verified fix commit + ASOF simulation run; deduped against the state-file/alerting cluster (edge-triggered alerts, unattended-job failure alert, instrument-the-failing-path) — adjacent failure modes, cross-linked instead of merged; kept commit hash + repo as provenance, no volatile ExampleApp facts.
- 2026-07-17 · ExampleApp MARKTBLICK P0-fixes · filed 2 pattern pages from one verified end-to-end run (unattended-job-failure-alert-on-output-channel, single-source-of-truth-for-mutable-facts) after deduping against the existing alerting cluster (adjacent but distinct → cross-linked, not merged); updated the twib project profile to the current MARKTBLICK state instead of filing operational facts as lessons; wiki-wide grep confirmed no other page carried the outdated claims; volatile detail left in the project's `.memory/`.

## Related pages

- [[role-verifier]]
- [[role-wiki-critic]]
