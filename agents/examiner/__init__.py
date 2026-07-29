"""The examiner: blind grading of a learner response against a frozen rubric.

INV-2 / CON-3: this package never imports `server/`, `dispatcher/`, `cli/` or
`channels/`. It is the one place model/network calls are allowed to live
(INV-1 keeps them out of `core/`).
"""
