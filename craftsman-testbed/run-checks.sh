#!/usr/bin/env bash
# Testbed fixture validation script.
# Verifies that each fixture has the structural elements its description claims to prove.
# Exit 0 = all pass, 1 = any fail.

set -uo pipefail

TESTBED="$(cd "$(dirname "$0")" && pwd)"
PASS=0; FAIL=0

ok()   { echo "PASS: $*"; PASS=$((PASS+1)); }
fail() { echo "FAIL: $*"; FAIL=$((FAIL+1)); }

pick_python() {
  # Some machines only have `python3` on PATH, others only `python`; on some
  # Windows setups `python3` is a non-functional Microsoft Store app-execution
  # alias — `command -v python3` finds it, but running it fails. So each
  # candidate is sanity-checked by actually running it, not just located.
  for pybin in python3 python; do
    if command -v "$pybin" >/dev/null 2>&1 && "$pybin" -c "import sys" >/dev/null 2>&1; then
      printf '%s' "$pybin"
      return 0
    fi
  done
  return 1
}

json_field() {
  # Usage: json_field <file> <dotted.key>
  # Returns the string value at the given key path, or empty string.
  local pybin
  pybin=$(pick_python) || { echo ""; return 0; }
  "$pybin" - "$1" "$2" <<'PY'
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    keys = sys.argv[2].split('.')
    for k in keys:
        d = d.get(k, {}) if isinstance(d, dict) else {}
    print(d if isinstance(d, str) else '')
except Exception:
    print('')
PY
}

# ---------------------------------------------------------------------------
# fixture: existing-node
# Proves: craftsman:init picks a CI-declared test command over npm-test default
# ---------------------------------------------------------------------------
PKG="$TESTBED/existing-node/package.json"
if [[ -f "$PKG" ]]; then
  SCRIPT=$(json_field "$PKG" "scripts.test")
  if [[ -n "$SCRIPT" && "$SCRIPT" != "echo \"Error: no test specified\"" && "$SCRIPT" != "test" ]]; then
    ok "existing-node: scripts.test = '$SCRIPT' (non-generic)"
  else
    fail "existing-node: scripts.test missing or generic (got: '$SCRIPT')"
  fi
  [[ -f "$TESTBED/existing-node/package-lock.json" ]] \
    && ok  "existing-node: package-lock.json present (npm lockfile)" \
    || fail "existing-node: package-lock.json missing"
  [[ -f "$TESTBED/existing-node/.github/workflows/ci.yml" ]] \
    && ok  "existing-node: .github/workflows/ci.yml present" \
    || fail "existing-node: .github/workflows/ci.yml missing"
else
  fail "existing-node: package.json missing"
fi

# ---------------------------------------------------------------------------
# fixture: existing-node-with-graph
# Proves: graphify detection works alongside Node stack detection
# ---------------------------------------------------------------------------
PKG2="$TESTBED/existing-node-with-graph/package.json"
GRAPH="$TESTBED/existing-node-with-graph/graphify-out/graph.json"
if [[ -f "$PKG2" ]]; then
  SCRIPT2=$(json_field "$PKG2" "scripts.test")
  if [[ -n "$SCRIPT2" ]]; then
    ok  "existing-node-with-graph: scripts.test = '$SCRIPT2'"
  else
    fail "existing-node-with-graph: scripts.test missing"
  fi
else
  fail "existing-node-with-graph: package.json missing"
fi
if [[ -f "$GRAPH" ]]; then
  if pybin=$(pick_python); then
    "$pybin" - "$GRAPH" <<'PY' && ok "existing-node-with-graph: graphify-out/graph.json is valid JSON" || fail "existing-node-with-graph: graphify-out/graph.json is not valid JSON"
import json, sys
with open(sys.argv[1]) as f:
    json.load(f)
PY
  else
    fail "existing-node-with-graph: no working python3/python found — cannot validate graph.json"
  fi
else
  fail "existing-node-with-graph: graphify-out/graph.json missing"
fi

# ---------------------------------------------------------------------------
# fixture: existing-python
# Proves: Poetry stack is detected; 'poetry run pytest' preferred over 'pytest'
# ---------------------------------------------------------------------------
PYPROJ="$TESTBED/existing-python/pyproject.toml"
if [[ -f "$PYPROJ" ]]; then
  if grep -q '\[tool\.poetry\]' "$PYPROJ"; then
    ok  "existing-python: pyproject.toml has [tool.poetry] section"
  else
    fail "existing-python: pyproject.toml missing [tool.poetry] section"
  fi
else
  fail "existing-python: pyproject.toml missing"
fi

# ---------------------------------------------------------------------------
# fixture: new-empty
# Proves: craftsman:init does not guess a stack when no markers are present
# ---------------------------------------------------------------------------
EMPTY_FAIL=0
for marker in package.json pyproject.toml Cargo.toml go.mod requirements.txt pom.xml build.gradle; do
  if [[ -f "$TESTBED/new-empty/$marker" ]]; then
    fail "new-empty: unexpected stack marker '$marker' found"
    EMPTY_FAIL=1
  fi
done
[[ $EMPTY_FAIL -eq 0 ]] && ok "new-empty: no stack markers present (correct for empty project)"

# ---------------------------------------------------------------------------
echo ""
echo "Testbed checks: $PASS passed, $FAIL failed."
[[ $FAIL -eq 0 ]]
