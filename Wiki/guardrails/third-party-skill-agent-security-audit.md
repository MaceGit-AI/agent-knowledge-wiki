# Third-party skills/agents: security-audit before adoption

**Summary**: Anything we pull from GitHub or other external sources — a skill, an agent/role brief, a prompt, a snippet — must pass a security audit **before** it is adopted into our system (global `~/.claude` or a project team). External catalogs are "hiring catalogs" we recruit from on demand; we do not bulk-install.

**Type**: guardrail
**Applies to**: any acquisition of external skills, agents, prompts, or code
**Owner**: the [[role-security]] runs/owns the audit
**Last updated**: 2026-06-18

---

## Rule

1. **Clone to scratch, never into our git.** Pull external repos into a throwaway area outside all our repos (e.g. `<SCRATCH_DIR>/`). Never commit third-party code/content into the wiki, the engine, or a project repo.
2. **Audit before adopt.** Before any item enters `~/.claude` or a `TEAM.md`, the security role checks for:
   - **Prompt injection / hidden instructions** (e.g. "ignore previous", instructions to exfiltrate, embedded URLs/credentials, invisible unicode).
   - **Exfiltration / phone-home** — does it send data out, fetch+execute remote code, or add network calls?
   - **Destructive or over-broad actions** — `rm -rf`, force-push, mass edits; tool scopes wider than the task needs.
   - **Secret handling** — does it read/log env/keys? (cross-check [[no-secrets-or-private-account-data]]).
   - **Supply chain & license** — pinned deps? permissive license? maintained source?
3. **Assimilate, don't paste.** Rewrite the useful idea **in our own words** into our skill/role/wiki format (shrinks the injection surface — see skill-smith). Record **provenance** (source repo + commit) and the **audit verdict** on the page.
4. **Recruit on demand.** We do not need every skill/agent up front. Adopt only what a real, current need calls for; leave the rest in the catalog for later re-recruiting.

## Why

External skills/agents are executable instructions for our agents. An unaudited one is an untrusted code dependency with prompt-injection reach into our whole system. Treating sources as hiring catalogs (audit → assimilate → verify) keeps us fast without inheriting someone else's risk.

## Related pages
- [[no-secrets-or-private-account-data]]
- [[machinery-sync-engine-template]]
