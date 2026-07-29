---
name: tool-surface-conventions
description: How to add or change an MCP tool in Anamnesis — naming, preconditions, the refusal shape, instrumentation, and keeping the teaching instruction files in step. Use when touching server/, adding a tool, adding a reason code, or changing anything a caller can pass.
---

# Tool surface conventions

The tool surface is the published interface between the teaching conversation and the learner state. It is also where the project's contribution lives: *ordering enforced by refusing preconditions*. Getting a refusal wrong doesn't produce a bug — it produces a claim that isn't true.

## The shape of a tool

Thin. One verb, one responsibility. A precondition attaches to a named tool, and that is what makes a refusal legible and measurable. If you find yourself adding an `action` discriminator to fold two tools into one, stop — that converts a tool-level gate into argument validation and weakens the mechanism.

The one exception is `get_state`, which is deliberately fat: DR-4 requires read-back to be a single call.

## Adding a tool

1. Add the row to `spec/design-spec.md` §4.1, including the **"may not be passed"** column. A restriction that isn't in that column doesn't exist.
2. Implement it in `server/`. Preconditions first, work second.
3. Add a contract test for the happy path **and** one per refusal.
4. Update `teaching/` — the instruction files are the other half of this interface. A tool the model doesn't know about is a tool that never gets called.
5. Run the `refusal-audit` subagent.

## The refusal shape

A refusal is a **successful** result, never a protocol error:

```json
{ "refused": true,
  "reason_code": "TOPIC_UNEVIDENCED",
  "message": "Topic 'Osmosis' has no recorded attempts.",
  "remedy": "Record at least one attempt with record_attempt(probe_id, response_text, answer_was_onscreen) before closing.",
  "blocking": { "topic_id": "top_19", "n_attempts": 0 } }
```

**`remedy` is the load-bearing field.** Policy-bound agents follow written rules unreliably; a refusal that names the next action converts a policy into something executable. A refusal without a remedy causes the caller to retry variations of the same wrong thing until its context is gone.

**Every refusal appends a `refused` event.** That is not logging — it is how bypass rate is computed (DR-6). A refusal that returns without appending silently removes the project's own measurement.

## What may never be a parameter

`verdict` · `route_quality` · `expressed_confidence` · `rubric` · `review_due` · `stability` · `difficulty` · any status or confidence field.

These are refused, **not ignored**. Silently dropping an unexpected parameter passes a sloppy test and reproduces the exact prototype failure the project exists to remove: a caller asserting a competence it has not evidenced, and the system going along with it.

`grade_attempt` takes `attempt_id` and nothing else. If you are tempted to add a second parameter, re-read spec §4.1 first.

## Naming

`verb_noun`, snake case, no prefix — the MCP server name already namespaces them. Renaming a tool is a breaking change to `teaching/` and to every stored `refused` event's `tool` field, so name it right the first time.
