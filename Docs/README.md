# Working on Anamnesis with Claude Code

How to drive the build with these documents. Read once before phase 0; come back for the failure recipes.

---

## 1. Install, once

The kit does nothing sitting in `Docs/Production/`. Copy it into the repo:

```bash
cd /Users/hamza/Code/Anamnesis
cp Docs/Production/claude/CLAUDE.md        ./CLAUDE.md
mkdir -p .claude
cp -r Docs/Production/claude/hooks         .claude/
cp -r Docs/Production/claude/agents        .claude/
cp -r Docs/Production/claude/skills        .claude/
cp    Docs/Production/claude/settings.json .claude/
cp -r Docs/Production/spec Docs/Production/tests Docs/Production/prompts ./
chmod +x .claude/hooks/*.sh
```

Keep `Docs/Production/` as the pristine copy. Edit the working copies; regenerate rather than hand-patch.

**Then verify in a real session, because a wrong hook event name fails silently:**

| Ask for | Should happen |
|---|---|
| Add `import httpx` to a file under `core/` | Blocked |
| Edit an existing file under `tests/contract/` | Blocked |
| An ordinary edit under `server/` | **Nothing fires** — this is the check people skip |
| "Run the boundary-audit subagent" | It launches |

Run `/doctor` too — it flags subagent name collisions, which are otherwise invisible.

---

## 2. The loop

**One phase per session. Always a fresh one.**

```
1. New session in the repo root
2. Paste the entire phase prompt from prompts/phase-NN-*.md
3. Let it work until it stops
4. Run the gate yourself — command AND manual check
5. Commit
6. New session for the next phase
```

The phase prompts are deliberately self-contained: they assume no memory. That's what makes step 1 safe and step 6 cheap.

---

## 3. Prompting

**Paste the phase prompt whole.** Don't summarise it, don't paste "the gist". The non-goals section is doing as much work as the goals — it's what stops the agent building phase 4 during phase 2.

**Don't paste the charter or the proposal.** The charter is ~500 lines and the spec already encodes every decision derived from it. Pasting it spends context re-deriving what's settled, and invites the agent to relitigate.

**Point, don't paste.** `@spec/design-spec.md` and `@tests/test-contract.md` let it read what it needs. The phase prompt already names the sections.

**When it asks a question the spec answers**, reply with the section, not the answer: *"spec §6, read it."* Answering directly teaches it to ask you instead of reading, and by phase 4 you're the bottleneck.

**When it says the spec and the charter disagree** — the charter wins and the spec is wrong. Stop, note it, fix the spec. The spec is derived; it has no independent authority.

---

## 4. The agentic features, and when each earns its keep

**Subagents** — three read-only auditors. Ask by name: *"Run the refusal-audit subagent."* Naming it beats describing it, since matching is on the `description` field.

| Subagent | Run it |
|---|---|
| `refusal-audit` | Before the phase 3 gate, and any time the tool surface changes. This one audits the contribution claim |
| `writer-audit` | Before every gate from phase 1 on, and whenever a derived value looks wrong |
| `boundary-audit` | When a phase touches more than one module |

They report and change nothing. That's deliberate — a subagent can't get your approval mid-task, so anything that could edit would either hang or act unreviewed. If one reports a finding, *you* decide; never tell the main session "do what the auditor said."

**Plan mode** (`shift+tab` to cycle, or `--permission-mode plan`) — read-only until you approve the plan. Worth it at the start of phases 3 and 4, where the design space is wide. Skip it for phases 1 and 2, which are tightly specified enough that planning is just latency.

**Skills** load themselves. `event-conventions` fires when you touch `core/`, `tool-surface-conventions` when you touch `server/`. You don't invoke them. Note the cost: a skill body **stays in context for the rest of the session**, so a session that trips both is meaningfully heavier — another reason phases don't share sessions.

**`acceptEdits`** is reasonable inside a phase once you trust the direction: the hooks are the real guardrail, not the permission prompts, and clicking approve forty times is how people end up skimming. Never use `bypassPermissions` here — the deny rules survive it, but nothing else does.

**Don't use agent teams.** Experimental, Opus-only, several times the tokens, and in-process teammates don't survive `/resume`. On a multi-week solo build the no-resume limitation alone disqualifies it.

---

## 5. Model and effort, per phase

Each phase prompt opens with a **Before you paste — setup only** block: the launch command, the slash commands to run in the session, and a `▼ Paste from here` marker so you know where the prompt itself begins. Work down that block, then paste everything below the marker.

Launch flags apply to that session only and don't overwrite your saved default — which is exactly what one-phase-per-session wants. `/model` and `/effort` typed in-session *do* save as your default, so prefer the launch flags.

| Phase | Launch with | Plan mode | Why |
|---|---|---|---|
| 00 gate | `--model opus --effort xhigh` | yes | Small code, high stakes. A wrong call invalidates everything after it |
| 01 log | `--model sonnet --effort high` | no | Tightly specified and mechanical |
| 02 memory | `--model sonnet --effort xhigh` | no | One state-machine edge an agent will try to simplify away |
| 03 tool surface | `--model fable --effort high` | **yes** | Largest phase, carries the contribution claim, spans more than a sitting |
| 04 candidates | `--model opusplan` | yes | Wide design space up front, long straightforward tail after |
| 05 dispatcher | `--model opus --effort xhigh` | yes | Integration-heavy, real-world failure modes |
| 06 paper/photo | `--model sonnet --effort high` | no | Three loosely coupled pieces |
| 07 trial | `--model sonnet --effort high` | no | SQL and a coverage sweep; the judgement is yours |

Default effort is `high` on every model that supports it, so `--effort high` is belt-and-braces — state it anyway, since effort persists across sessions once you set it and you may not remember what the last phase left behind.

**Effort, briefly.** `xhigh` buys deeper reasoning at higher spend. `max` exists but is session-only and prone to overthinking — don't reach for it by default. For one-off depth without changing the session setting, put the word `ultrathink` in that single message; other phrasings like "think hard" are just ordinary text.

**Subagents carry their own model** in frontmatter: `writer-audit` and `boundary-audit` run Sonnet, `refusal-audit` runs Opus because it judges whether the contribution claim is actually supported. Don't set `CLAUDE_CODE_SUBAGENT_MODEL` — it overrides all three.

### The classifier caveat, because this is a medical project

Fable 5 and Opus 5 both run safety classifiers for biology content, and they behave differently when one fires:

- **Fable 5** — a biology flag re-runs the request on Opus 5, and the session continues there.
- **Opus 5** — a biology flag **ends in a refusal**. Opus 5 runs its own biology classifiers with no fallback beneath them.

Phase 0 feeds physiology and pharmacology material to a grader, and phase 6 sends handwritten medical answers to a vision model. Those are the two most likely to trip it. It can also fire on the *first* request of a session, before you've sent anything unusual, because that request carries your CLAUDE.md and git status — a repo full of medical rubrics can trip it on context alone.

If it happens:

- `claude --safe-mode` disables CLAUDE.md, skills, hooks and MCP, which tells you whether your customisations are the trigger or the material itself is.
- `/config` → turn off *"switch models when a message is flagged"* to be asked each time rather than silently moved.
- Working on Fable and being moved to Opus 5 mid-phase is survivable. Starting a medical-content phase on Opus 5 and hitting a refusal is not, so prefer Fable for anything that handles the material in bulk.

This is expected routing for the domain, not a flag on your account.

## 6. When a hook fires

A block is information, not an obstacle. The message names the invariant, the spec section, and what to do instead.

**Read what it said, then fix the code.** Do not tell the agent to work around it — an agent that's been told once to route around a hook will do it again unprompted, and you've disabled the enforcement without disabling the hook.

If a hook fires on something genuinely legitimate, that's a spec bug. Note it, unblock yourself by fixing the spec and regenerating — not by editing the hook. A hook edited to pass today's case stops catching tomorrow's.

**Never set `disableAllHooks`**, and watch for `.claude/settings.local.json` — it's gitignored and outranks `settings.json`, so it's the quiet way enforcement dies. `permissions.deny` is the exception: it wins from any scope, which is why the hard prohibitions live there.

---

## 7. The gate

**Run it yourself. Every time.**

Not "did the tests pass?" — run the command, then do the manual check the phase prompt describes. An agent reporting its own tests green is structurally the same mistake as a grader that holds the conversation it's grading. That's the failure this entire project exists to remove; don't reintroduce it one layer up.

For CI later: run the test command directly. Don't gate through `claude -p --bare` — `--bare` skips hook discovery, so you'd be gating with the enforcement switched off.

---

## 8. Failure recipes

**Context runs out mid-phase.** Don't `/compact` and push on — compaction summarises project rules away exactly when the session is long enough to need them. Commit what works, start fresh, paste the phase prompt plus a short "already done: X, Y. Remaining: Z."

**The gate fails twice for different reasons.** Stop and re-read the spec section it covers. Two unrelated failures in one phase usually means the spec is ambiguous there, not that the agent is careless.

**The agent wants to edit a contract test.** It's blocked, and it's the right block. A failing contract test means the implementation is wrong. If the *requirement* genuinely changed, that's a charter edit and a kit regeneration — never a test edit.

**The agent starts a phase you didn't ask for.** The prompt's non-goals section didn't survive. Stop it, start fresh, paste the prompt whole.

**Replay verification fails.** Read `.claude/skills/event-conventions/SKILL.md` — it lists the four causes in likelihood order. Never fix it by regenerating the expected state.

---

## 9. Two things you'll hit

**The charter is a version behind.** It still frames learner modelling and ambient delivery as contributions, still describes an in-repo tutor and a web UI — all cut. Six requirements (`DR-1`…`DR-6`, the refusal layer that's now the central claim) live only in the spec. If the agent cites a charter FR that contradicts the spec, check spec §0 first: it may be one of the cut ones.

**Phase 0 can end the project.** If SC-1 or SC-4 misses its threshold, the architecture changes and nothing else runs. That's the design, not a formality. Don't reorder it to reach the interesting part.
