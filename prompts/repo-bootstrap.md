# Repo bootstrap — connect to GitHub

> Paste this into the current session. Self-contained: assume no memory.
>
> **A first push to a public remote is close to irreversible.** Git history is permanent, and a leaked credential must be *rotated*, not merely deleted. There is a mandatory stop before the push.

---

## Before you paste — setup only

No model change needed; continue in the current session. If you have started a new one:

```bash
claude --model sonnet --effort high
```

| Command | Why |
|---|---|
| `/status` | Confirm what model and effort you're on |
| `/permissions` | This phase runs git commands that touch a remote. Know what's auto-approved before it starts |

---

**▼ Everything below this line is the prompt. Paste from here.**

---

## Goal

Get the Phase 0a work onto the default branch, connect the GitHub remote, and push — without publishing anything that should not be public.

Remote: `https://github.com/Hamza-Xoho/Anamnesis`

## State you are starting from

- Local repo at `/Users/hamza/Code/Anamnesis`, default branch `master`. GitHub's default is `main`.
- Phase 0a is committed on branch `worktree-phase0-examiner`, in a worktree at `.claude/worktrees/phase0-examiner`. **It is not on `master`.**
- `tests/fixtures/frozen/*.yaml` were reset to empty schema stubs. Earlier content in those files was illustrative, not real evaluation data, and must not be restored.
- No remote is configured yet.

Verify each of these rather than trusting the list.

## Do this, in order

1. **Merge Phase 0a onto the default branch.** Fast-forward if possible; do not rebase, do not squash. The commit message history is the build record.
2. **Retire the worktree** — `git worktree remove`, then delete the merged branch. Leave `.claude/worktrees/` clean.
3. **Commit the fixture stubs** and anything else outstanding in the working tree.
4. **Reconcile the branch name.** Rename `master` to `main` locally so it matches GitHub's default. Do this before adding the remote, not after.
5. **Audit `.gitignore`** — see below.
6. **Run the pre-push audit** — see below. **Then stop.**
7. Only after I approve: add the remote and push.

## `.gitignore` audit

Confirm every one of these is ignored, and add any that is not:

```
.env
.env.*
data/
__pycache__/
*.pyc
.DS_Store
.claude/settings.local.json
.claude-flow/
.claude/worktrees/
```

Then run `git status --ignored --short` and confirm nothing sensitive is staged.

## Pre-push audit — report, do not act

Walk everything that would be pushed. For each category below, list the specific files and stop for my decision. Do not judge on my behalf, and do not push while any item is unresolved.

**1. Credentials.** Any API key, token, or `.env` content — including in git *history*, not just the working tree. Check with `git log -p | grep` for `sk-ant`, `ANTHROPIC_API_KEY`, `TELEGRAM`, `token`, `secret`. If anything is found in history, say so plainly: deleting the file is not sufficient and the credential must be rotated.

**2. Personal learning data.** `tests/fixtures/frozen/` will eventually hold my own answers, including my mistakes. `data/` holds my actual learning history. State clearly what is currently present and what would become public.

**3. Unsubmitted academic work.** `Docs/Proposals/` contains a project proposal not yet submitted. Publishing it before submission can cause an originality checker to flag my own repository as a source against me. Flag it and let me decide.

**4. Third-party data.** Any answer sourced from another person (`source: peer-answer`). Their consent to my using it is not consent to publish it.

Finish the audit with a single question: **is the GitHub repo public or private?** The right answer for categories 2–4 depends entirely on that, and I have not told you.

## Not in this phase

- **Do not push before I approve the audit.** Not as a final step, not as a convenience.
- **Do not force-push, rebase, squash, or rewrite history.** Ever, on this repo.
- Do not create a `LICENSE`, `README.md`, CI workflow, issue templates, or branch protection. If you think one is needed, say so and stop.
- Do not touch `Docs/Production/` — it is the pristine kit copy and stays byte-identical to what was generated.
- Do not add, edit, or restore any content in `tests/fixtures/frozen/`. It is mine to write.
- Do not `git add -A` blindly. Stage deliberately and say what you staged.

## Definition of done

1. Phase 0a is on `main`, and `agents/examiner/` plus `tests/contract/phase0/` exist there.
2. The worktree is removed and the merged branch deleted.
3. `.gitignore` covers every line above; `git status` is clean.
4. The pre-push audit is reported in full and every item resolved by me.
5. `git push -u origin main` succeeds, and `git log --oneline origin/main` matches local.
6. `pytest tests/contract/phase0/ -v` still gives 7 passed, 3 skipped after the merge.

## Gate

```
git log --oneline --graph -10 && git status --short && pytest tests/contract/phase0/ -v
```

Then confirm by hand: **open the repo on GitHub in a browser and look at it.** Check the file tree against the audit — specifically that no `.env`, no `data/`, and nothing under `.claude/settings.local.json` is there. A push that succeeded is not the same as a push that was correct.

## Stop

When the definition of done is met, stop and report. Do not begin Phase 1.
