#!/usr/bin/env bash
# freeze-contract-tests.sh — PreToolUse on Write|Edit|MultiEdit|Bash
#
# Counters test erosion. Agents weaken or delete failing tests to make a phase
# pass, and a deleted test reports GREEN — which silently voids every
# invariant-tier row in the contract.
#
# CREATING a new contract test file is allowed: each phase writes its own tests
# first, and must be able to. MODIFYING or DELETING one that already exists is
# blocked.
#
# The unfreeze path is a human editing .claude/settings.json. Deliberately not
# an env var or a marker file — anything the agent can write is theatre.
set -euo pipefail
command -v python3 >/dev/null || { echo "HOOK ERROR: python3 not found; cannot verify the test freeze." >&2; exit 2; }
trap 'echo "HOOK ERROR: freeze check did not complete; blocking rather than passing." >&2; exit 2' ERR

payload=$(cat)

field() {
  printf '%s' "$payload" | python3 -c '
import json, sys
d = json.load(sys.stdin)
if sys.argv[1] == "tool_name":
    sys.stdout.write(str(d.get("tool_name") or "")); raise SystemExit
ti = d.get("tool_input") or {}
sys.stdout.write(str(ti.get(sys.argv[1]) or ""))
' "$1"
}

tool=$(field tool_name)

deny() {
  cat >&2 <<'MSG'
BLOCKED — the Anamnesis contract tests are frozen.

They encode the charter's acceptance criteria verbatim. A failing contract test
means the IMPLEMENTATION is wrong, not the test. Weakening one converts a red
build into a green one that asserts nothing.

Do instead:
  - Fix the implementation so the test passes as written.
  - If the test looks wrong, re-read the spec section it cites. Two unrelated
    failures in one phase usually means the spec is ambiguous, not that the
    test is bad.
  - If the REQUIREMENT genuinely changed: stop and report it. The human updates
    the charter and regenerates the kit. Do not edit around a red test.

Creating a NEW contract test file is allowed — that is how each phase starts.
MSG
  exit 2
}

case "$tool" in
  Bash)
    cmd=$(field command)
    # Deletion, renaming, reverting, or truncating a frozen test.
    if grep -qE '(\brm\b|\bmv\b|git[[:space:]]+rm\b|git[[:space:]]+(checkout|restore)\b|\btruncate\b|>[[:space:]]*[^|]*)[^|]*tests/contract/' <<<"$cmd"; then
      deny
    fi
    ;;
  Write|Edit|MultiEdit)
    path=$(field file_path)
    [ -z "$path" ] && exit 0
    case "$path" in
      *tests/contract/*)
        # New file → allow. Existing file → block.
        [ -e "$path" ] && deny
        ;;
    esac
    ;;
esac

exit 0
