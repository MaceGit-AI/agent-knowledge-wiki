// SessionStart hook: print loop-awareness context.
// Stdout is added to the session context. Must never throw — wrap everything.
import { existsSync } from 'node:fs';
import { join } from 'node:path';

try {
  const cwd = process.cwd();
  const hasAgents = existsSync(join(cwd, 'AGENTS.md'));
  const wikiIndex = '<WIKI_DIR>/Wiki/index.md';

  const lines = ['[karpathy] 3-layer loop active: SPEC → VERIFIER → ENVIRONMENT.'];
  if (hasAgents) {
    lines.push('This repo has AGENTS.md — read it for specs/SPEC.md, VERIFIER.md, ENVIRONMENT.md.');
  } else {
    lines.push('No AGENTS.md here — consider /karpathy-init to scaffold the 3 layers.');
  }
  lines.push(`Experience library: ${wikiIndex} (recall before, /learn after a green verify).`);
  console.log(lines.join(' '));
} catch {
  // Never fail a session start because of this hook.
}
