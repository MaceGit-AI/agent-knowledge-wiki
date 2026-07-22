# Guardrail — No unverified assumptions

**Summary**: Agents must not silently assume missing facts, user intent, project
boundaries, source meaning, architecture rules, or import decisions. They must
verify from evidence or ask the human before acting on the unknown.

**Trigger**: The owner explicitly required that the system must move forward
without circular rework, but assumptions are allowed only after consultation.

**Scope**: All Claude, Codex/GPT, and future agent work on this knowledge
library; especially project mapping, GPT memory imports, cross-repo distillation,
knowledge promotion, ADRs, guardrails, commits, and pushes.

**Last updated**: 2026-06-18

---

## Rule

Do not treat an assumption as a fact.

Before acting on a missing or ambiguous point, an agent must either:

- verify it from a cited source, repository file, command result, existing wiki
  page, or explicit human statement; or
- ask the human a focused question and wait for the answer.

This includes:

- which repository or project is in scope;
- whether two folders are the same project or separate projects;
- which project is current vs legacy;
- what a source file means when the source is ambiguous;
- whether a lesson is verified enough for `Wiki/experience/`;
- whether GPT memory or chat-export material may be imported;
- whether sensitive or private material is safe to store;
- whether a missing fact should become a wiki claim, decision, or guardrail.

## Momentum rule

Avoid circular work. If a fact cannot be verified after checking the relevant
source material:

1. stop the dependent branch;
2. state the exact missing fact;
3. ask one focused question;
4. continue only with independent safe work that does not rely on the unknown.

Do not repeatedly reread the same files or invent a default to avoid asking.

## Working hypotheses

Working hypotheses are allowed only when clearly labeled as hypotheses. They may
live in a session journal or temporary analysis, but they must not be promoted to
project profiles, knowledge pages, experience pages, ADRs, or guardrails until
verified or explicitly confirmed by the human.

## Required language

Use explicit labels:

- `Verified:` for facts backed by a source.
- `Unknown:` for facts not yet established.
- `Needs human confirmation:` for decisions or interpretations that require the
  owner.
- `Hypothesis:` only for temporary reasoning that will not be acted on without
  verification.

## Escalation

Stop and ask the human when:

- the next action would depend on an unverified assumption;
- sources conflict;
- a project boundary is unclear;
- an import could mix projects or leak private material;
- verification is not possible from available files or commands.

## Related pages

- [[repo-boundary-llm-knowledge-library]]
- [[no-secrets-or-private-account-data]]

