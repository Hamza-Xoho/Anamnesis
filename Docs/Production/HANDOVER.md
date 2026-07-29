# Anamnesis — Build Kit

Everything needed to build Anamnesis with a coding agent. Generated 2026-07-27 from `anamnesis-charter.md` v0.2.0 and `anamnesis-proposal.md` v0.2.0, **with the proposal governing the architecture**.

Read this file first. It is the whole operating manual — you are not meant to come back to the generating skill.

## What's here

| Path | What it is | When you touch it |
|---|---|---|
| `spec/design-spec.md` | The *how* — 20 decisions, module boundaries, event schema, tool surface, refusal semantics | Read before phase 1; update only by regenerating |
| `tests/test-contract.md` | Every acceptance criterion as a named test, in EARS form, per phase | Each phase writes its own rows first |
| `prompts/phase-00…07` | One self-contained brief per phase | Paste into a fresh session, in order |
| `claude/CLAUDE.md` | Always-on project rules, 48 lines | Copy to repo root |
| `claude/settings.json` | Wires the hooks and the deny rules | **Without this the hooks do nothing** |
| `claude/hooks/` | Four hooks: block, sweep, freeze, inject | Install once; leave on |
| `claude/agents/` | Three read-only auditors | Invoke before gates |
| `claude/skills/` | Event and tool-surface conventions | Loaded on demand |

## Setup, once

0. **`git init`, if you haven't.** Phase 0's frozen evaluation set is frozen *by being committed*, so the gate cannot complete in a non-repo. Add `.env` and `data/` to `.gitignore` before the first commit.
1. Copy `claude/CLAUDE.md` to the repo root.
2. Copy `claude/settings.json`, `claude/hooks/`, `claude/agents/`, `claude/skills/` into `.claude/`. Then `chmod +x .claude/hooks/*.sh`. **The scripts do nothing until `settings.json` wires them** — shipping the scripts alone looks complete and enforces nothing.
3. Copy `spec/` and `tests/` into the repo. The agent reads them every phase, so they must be in the working tree, not a folder on your desktop.
4. **Verify each hook in a real session.** They were verified as scripts during generation (see below), but a wrong event name fails *silently*, so only a live session proves the wiring:
   - Ask it to add `import httpx` to a file under `core/` → must be blocked.
   - Ask it to edit an existing file under `tests/contract/` → must be blocked.
   - Ask it to make an ordinary edit under `server/` → **nothing** should fire. This is the check people skip, and false positives are what get `disableAllHooks` switched on.
   - Start the `boundary-audit` subagent → must launch. A bad `tools:` entry is a hard launch failure, unlike a hook typo.
5. Hooks parse with `python3`, not `jq` — Python 3.12 is already a project dependency, so there is nothing extra to install. All four **fail closed**: if `python3` goes missing or a payload is malformed, they block rather than pass.
6. **Note where the freeze is unfrozen: `.claude/settings.json`.** That is deliberate. It must sit somewhere the agent cannot reach, so unfreezing is an act you take on purpose.

## The phases

| Phase | Delivers | `must` requirements |
|---|---|---|
| **00 — the gate** | Grading harness + frozen evaluation set | FR-3, FR-4, FR-5 |
| 01 — the log | Append-only log, deterministic reducer, replay | FR-6 |
| 02 — memory and the two lanes | FSRS-6 per probe, concept rollup, due vs candidate | FR-7, FR-9, FR-22 |
| 03 — the tool surface | MCP server, gated preconditions, refusals, digest | FR-2, DR-1, DR-2, DR-3, DR-4 |
| 04 — candidates, export, instrumentation | Generators, ranking, Obsidian, CLI, bypass rate | FR-10, FR-11, DR-6 |
| 05 — the dispatcher | Telegram, scheduling, reply grading, liveness | FR-12, FR-13, DR-5 |
| 06 — paper, photo, calibration | Sheets, handwritten ingestion, calibration | — (all `should`) |
| 07 — trial and evaluation | Four-week sole use, measured KPIs | — |

**Phase 0 can end the project.** If SC-1 or SC-4 misses its threshold, the architecture changes and nothing else runs. That is the charter's design, not a formality — it is small, cheap, and the only phase that can invalidate the rest. Do not reorder it to get to the interesting part.

## Running a phase

1. Start a **fresh session**. Phase prompts assume no memory; a stale context carries the previous phase's assumptions.
2. Paste the phase prompt.
3. Let it work to the stop condition.
4. **Run the gate yourself.** Not "did the tests pass?" — run the command, then do the manual check. An agent reporting its own tests passed is structurally the same mistake as a grader holding the conversation it is grading. That is the failure this whole project exists to remove; do not reintroduce it at the build layer.
5. Commit only after the gate passes.

## When a gate fails

The phase is not done. Do not proceed and fix later — the next phase builds on the broken thing, and the eventual fix touches both, in a diff too large to review. The temptation is strongest when you are tired, which is exactly when the cost is highest.

Report the failure back into the same session if the context is still good. Start fresh with the phase prompt plus a description of the failure if it isn't.

**If a gate fails twice for different reasons, stop and re-read the spec section it covers.** Two unrelated failures in one phase usually means the spec is ambiguous there, not that the agent is careless.

## When the charter changes

**Re-run `project-buildkit` and diff the spec. Do not hand-patch this kit.**

A hand-patched kit drifts from the charter, and then the tests assert something nobody decided — worse than no tests, because it looks like coverage. The spec's decision table is dated and append-only for exactly this reason: a re-run can see what the first interview settled and ask only about what moved.

## Which hook enforces what

A hook whose purpose has been forgotten gets deleted at the first inconvenience.

| Hook | Event | Enforces | From |
|---|---|---|---|
| `block-boundary-violation.sh` | `PreToolUse` on `Write\|Edit` | INV-1, 2, 3, 5, 7 — preventive | spec §2; CON-1, CON-3, CON-12 |
| `sweep-boundaries.sh` | `PostToolUse` on `Write\|Edit\|MultiEdit` | Same five, reading from disk | Backstop: `Edit` shows a hook only the added fragment, so pre-existing violations are invisible to the blocking check |
| `freeze-contract-tests.sh` | `PreToolUse` on `Write\|Edit\|MultiEdit\|Bash` | INV-6 — creation allowed, modification and deletion blocked | Agents delete failing tests, and a deleted test reports green |
| `inject-invariants.sh` | `SessionStart` | Re-states all seven deterministically | Compaction summarises project rules away in exactly the long sessions where they matter |

Every hook was fired during generation and observed to block on a violation, stay silent on an unrelated edit, and exit 2 when its dependency was removed.

## Decisions taken as defaults

All twelve interview questions were answered with the recommendation. These are the ones with real consequences:

- **The dispatcher writes directly to the log**, through the one shared append module (D-3). "Sole writer" therefore means *the teaching layer cannot write*, not *one process*. Chosen so the dispatcher owns its own lifecycle — an MCP stdio server dies with its client, and a dispatcher that dies when you close Claude is the prototype's failure with extra steps.
- **Derived state is materialised, not computed on read** (D-5). NFR-3 is satisfied by a replay-equality test, not by refusing to cache.
- **A refusal is a successful result, not a protocol error** (D-7). If this is ever changed, DR-6 stops being measurable — the bypass rate is computed from `refused` events.
- **Route failure emits a candidate, not a probe** (D-10). This resolves the charter's own §15 open question. A spawned probe would need a rubric, rubrics need a model call, and `core/` may make none.
- **Concept merges are proposed, never automatic** (D-9). An automatic merge is an assertion about your knowledge, which is the thing CON-1 exists to prevent.
- **Photos are transcribed then graded as text** (D-14), so one examiner path and one pinned model survive, and a wrong grade tells you immediately which half failed.
- **Anki stays external** (D-11, resolving Q-5). Atoms are events, exported to a file your existing `anki` skill consumes. No AnkiConnect, no runtime dependency.

## Deliberately not covered

Charter non-goals: no multi-user, accounts, sync or cloud storage · no corpus RAG or document Q&A · no content library or pre-authored curricula · no mobile app beyond the ambient channel · no bulk review grinding · no note authored from anything but retrieval · no fine-tuned models in v1.

Cut when the proposal took precedence over the charter: **FR-1** (the tutor moves out of the service entirely — teaching is not reimplemented), **FR-20** (brain view), **FR-21** (Anki and vault import as seed state), and the **local web UI**, replaced by the tool surface, `anamnesis status`, and Telegram.

Not a build phase: **FSRS parameter fitting (Q-8)**. It needs 2–3 months of real `(probe, verdict, delta_t)` history after phase 2, then a comparison of log-loss against defaults. If personal fitting is worse than defaults, hold defaults.
