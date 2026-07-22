#!/usr/bin/env bash
# Refresh this content-free engine template FROM the live system, re-applying the
# same genericization used to build it. Run after you change the system machinery
# (WIKI_PROTOCOL / Templates / roster / guardrails / ~/.claude agents-skills-commands
# / the recall MCP / the gpt-chat sparring MCP) so the engine and the live wiki stay in sync.
#
# No user paths are baked in — pass them as env vars:
#   WIKI_SRC=/path/to/live/wiki   RECALL_SRC=/path/to/knowledge-recall-mcp   [GPTCHAT_SRC=/path/to/gpt-chat-mcp]   [CLAUDE_HOME=~/.claude]   ./sync.sh
#
# After it runs: review `git diff`, then commit + push the engine repo.
set -euo pipefail
ENGINE="$(cd "$(dirname "$0")" && pwd)"
WIKI_SRC="${WIKI_SRC:?set WIKI_SRC to the live wiki repo root}"
RECALL_SRC="${RECALL_SRC:-}"  # V2: recall code maintained in-repo (recall-mcp/); external source optional
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"

echo "engine : $ENGINE"; echo "wiki   : $WIKI_SRC"; echo "recall : $RECALL_SRC"; echo "claude : $CLAUDE_HOME"

# --- 1) machinery (~/.claude) ---
rm -rf "$ENGINE/claude/agents" "$ENGINE/claude/skills" "$ENGINE/claude/commands"
cp -r "$CLAUDE_HOME/agents" "$CLAUDE_HOME/skills" "$CLAUDE_HOME/commands" "$ENGINE/claude/"
cp "$CLAUDE_HOME/CLAUDE.md" "$ENGINE/claude/"
mkdir -p "$ENGINE/claude/scripts"
for s in session-start.mjs failure-recall.mjs learn-reminder.mjs; do
  cp "$CLAUDE_HOME/scripts/$s" "$ENGINE/claude/scripts/" 2>/dev/null || true; done
# drop any project-specific agents that shouldn't ship in the pool template
rm -f "$ENGINE/claude/agents/sme-"*.md "$ENGINE/claude/agents/data-scientist.md" 2>/dev/null || true

# --- 2) wiki engine files (ALLOWLIST — content layers are never copied) ---
cp "$WIKI_SRC/WIKI_PROTOCOL.md" "$WIKI_SRC/Claude.md" "$WIKI_SRC/AGENTS.md" "$ENGINE/"
rm -rf "$ENGINE/Templates"; cp -r "$WIKI_SRC/Templates" "$ENGINE/"
rm -rf "$ENGINE/Wiki/roster"; cp -r "$WIKI_SRC/Wiki/roster" "$ENGINE/Wiki/"
for m in karpathy-loop-and-agent-discipline skill-and-agent-probation-lifecycle team-coached-retrospective-loop cascaded-agent-memory; do
  cp "$WIKI_SRC/Wiki/experience/methodology/$m.md" "$ENGINE/Wiki/experience/methodology/" 2>/dev/null || true; done
for g in no-secrets-or-private-account-data parallel-agent-collaboration repo-boundary-llm-knowledge-library machinery-sync-engine-template third-party-skill-agent-security-audit no-unverified-assumptions stay-on-the-primary-thread gpt-export-import-triage third-party-model-gate; do
  cp "$WIKI_SRC/Wiki/guardrails/$g.md" "$ENGINE/Wiki/guardrails/" 2>/dev/null || true
done
mkdir -p "$ENGINE/addons/wiki-graph"
cp "$WIKI_SRC/addons/wiki-graph/wiki-graph.py" "$ENGINE/addons/wiki-graph/"  # addon code only; generated .html stays git-ignored
# machinery ADRs (design decisions about this system itself, not project content)
cp "$WIKI_SRC/Wiki/adr/0002-team-coached-self-improvement-loop.md" "$ENGINE/Wiki/adr/" 2>/dev/null || true
for k in agent-orchestration-options api-resilience-and-rate-limits local-recall-engine; do
  cp "$WIKI_SRC/Wiki/knowledge/$k.md" "$ENGINE/Wiki/knowledge/" 2>/dev/null || true; done
cp "$WIKI_SRC/Wiki/experience/environments/cdp-debug-electron-desktop-apps.md" "$WIKI_SRC/Wiki/experience/environments/package-local-mcp-server-as-mcpb.md" "$ENGINE/Wiki/experience/environments/" 2>/dev/null || true
cp "$WIKI_SRC/Wiki/experience/verifiers/dotnet-test-fast-single-class.md" "$ENGINE/Wiki/experience/verifiers/" 2>/dev/null || true
cp "$WIKI_SRC/Wiki/experience/patterns/appdata-config-local-override.md" "$ENGINE/Wiki/experience/patterns/" 2>/dev/null || true

# --- 3) recall MCP code (keep the engine's genericized README/DEPLOY) ---
cp "$RECALL_SRC"/{server.py,requirements.txt,bootstrap.ps1,bootstrap.sh,.gitignore,.gitattributes} "$ENGINE/recall-mcp/" 2>/dev/null || true
python - "$ENGINE/recall-mcp/server.py" <<'PY'
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
s = s.replace('lightweight hybrid recall over the LLM Knowledge Library Wiki.',
              'lightweight hybrid recall over a markdown knowledge wiki.')
s = re.sub(r'Replicates the proven recipe from the LLM WIKI engine.*?no API key, our own\.',
           'Proven recipe (FTS5 + FastEmbed embeddings + sqlite-vec + Reciprocal-Rank-Fusion),\n'
           'local-first, no API key. Point it at your wiki via the WIKI_DIR env var.', s, flags=re.S)
s = s.replace('WIKI_DIR = Path(os.environ.get("WIKI_DIR", r"D:/Sources/LLM Knowledge Library Wiki/Wiki"))',
              '# Default points at the sibling Wiki/ in this repo; override with the WIKI_DIR env var.\n'
              'WIKI_DIR = Path(os.environ.get("WIKI_DIR", str(Path(__file__).resolve().parent.parent / "Wiki")))')
open(p, 'w', encoding='utf-8').write(s)
PY

# --- 3b) gpt-chat sparring MCP (cross-model second opinion; GPT-side wiki tools
#         are sandboxed to GPT_MCP_WIKI_DIR — part of the engine since 17.07.2026) ---
GPTCHAT_SRC="${GPTCHAT_SRC:-}"
if [ -n "$GPTCHAT_SRC" ] && [ -f "$GPTCHAT_SRC/server.mjs" ]; then
  mkdir -p "$ENGINE/addons/gpt-chat-mcp"
  cp "$GPTCHAT_SRC/server.mjs" "$GPTCHAT_SRC/README.md" "$ENGINE/addons/gpt-chat-mcp/"
fi

# --- 4) genericize paths + project names (skip server.py for the WIKI path: handled above) ---
# EDIT THIS MAP for your own system: map every local path / project codename that can
# appear in your live wiki or ~/.claude files to a neutral placeholder. The examples
# below show the pattern — replace them with your real paths and project names.
find "$ENGINE" -type f \( -name '*.md' -o -name '*.mjs' \) -not -path '*/.git/*' -print0 | xargs -0 sed -i \
  -e 's|/path/to/live/wiki|<WIKI_DIR>|g' \
  -e 's|/path/to/your/api-key-file|<KEY_FILE>|g' \
  -e 's|/path/to/gpt-chat-mcp|<GPTCHAT_MCP_DIR>|g' \
  -e 's|/path/to/recall-mcp|<RECALL_MCP_DIR>|g' \
  -e 's|/path/to/knowledge-wiki-engine|<ENGINE_DIR>|g' \
  -e 's|/path/to/scratch|<SCRATCH_DIR>|g' \
  -e 's|/path/to/backups|<BACKUP_DIR>|g' \
  -e 's|/home/yourname/.claude|~/.claude|g' \
  -e 's|\bYourProjectCodename\b|ExampleApp|g'

# --- 5) links to pages not shipped in the template: drop dangling [[bullets]],
#        de-link inline [[refs]] to plain text ---
python - "$ENGINE" <<'PY'
import os, re, glob, sys
root = sys.argv[1]; wiki = os.path.join(root, 'Wiki')
pages = {os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(wiki, '**', '*.md'), recursive=True)}
def shipped(target): return target.strip().split('/')[-1] in pages
def delink(m):
    if shipped(m.group(1)): return m.group(0)
    return m.group(2) if m.group(2) else m.group(1).strip().split('/')[-1]
for f in glob.glob(os.path.join(wiki, '**', '*.md'), recursive=True):
    out = []
    for ln in open(f, encoding='utf-8').read().splitlines(keepends=True):
        m = re.match(r'^\s*-\s*\[\[([^\]|#]+)', ln)
        if m and not shipped(m.group(1)):
            continue
        # [[target]] / [[target#anchor]] / [[target|label]] -> label/target as plain text
        out.append(re.sub(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]', delink, ln))
    open(f, 'w', encoding='utf-8').write(''.join(out))
PY

# --- 6) verify: no leftover user paths/names, no broken internal links, no secrets ---
cd "$ENGINE"; fail=0
# extend this pattern with your own user dirs / project codenames
echo "== leftover user paths/names ==";  grep -rInE "D:[/\\]+Sources|C:[/\\]+Users|/home/yourname|\bYourProjectCodename\b" --include='*.md' --include='*.mjs' . && fail=1 || echo "  clean"
echo "== broken internal links =="; find Wiki -name '*.md' | xargs -n1 basename | sed 's/\.md$//' | sort -u > /tmp/_pages.txt
broken=0
while read -r t; do
  [ -z "$t" ] && continue
  grep -qx "$t" /tmp/_pages.txt || { echo "  BROKEN: [[$t]]"; broken=1; }
done < <(grep -rhoE '\[\[[^]]+\]\]' Wiki/ | sed -E 's/\[\[([^]|#]+).*/\1/;s#.*/##' | sort -u)
if [ "$broken" -eq 0 ]; then echo "  clean"; else fail=1; fi
echo "== done. review 'git diff', then commit + push =="
git status --short
exit $fail