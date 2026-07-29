# SYNTHETIC FIXTURES — mechanism tests only (Phase 0a)

**These are hand-authored, deliberately artificial inputs. They are NOT the
evaluation set and MUST NOT be used to measure grader quality.**

They exist only to exercise *code paths* for the Phase 0a mechanism tests
(FR-3, FR-4, FR-5, NFR-7): "does the plumbing hold?" — not "is the grader good?".
A leak in a code path leaks regardless of who wrote the text, so synthetic text
is legitimate here.

The tokens (`alpha`, `beta`, `gamma`, `delta`) are nonsense on purpose, so no one
can mistake this for real learner material. The deterministic offline grader
(`agents.examiner.client.DeterministicClient`) matches claims by keyword overlap,
so these fixtures are written to make that matching deterministic and obvious.

The real, frozen evaluation set for the Phase 0b *measurement* (SC-1, SC-4, κ)
lives in `../frozen/` and must come from real learner work — see that folder's
README. It does not exist yet; 0b is blocked until a human delivers it.
