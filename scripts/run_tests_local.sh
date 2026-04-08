#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Prefer a CI-supported Python (3.10–3.13); 3.14+ often breaks Django 4.2 yet.
PYBIN="${PYBIN:-}"
for try in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$try" >/dev/null 2>&1; then
    PYBIN="$try"
    break
  fi
done
if [[ -z "$PYBIN" ]]; then
  echo "No python3 found." >&2
  exit 1
fi
ver="$("$PYBIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "${ver%%.*}" -eq 3 ]] && [[ "${ver#*.}" -ge 14 ]]; then
  echo "Warning: Python $ver is not in the project's CI matrix (3.8–3.13). Install 3.12 for best results." >&2
fi

if [[ ! -d .venv ]]; then
  "$PYBIN" -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate
pip install -q -U pip
pip install -q -e ".[test]" "django~=4.2.0"

export DJANGO_SETTINGS_MODULE=tests.settings

MODE="${1:-sqlite}"
if [[ "$MODE" != "sqlite" && "$MODE" != "postgres" ]]; then
  echo "Usage: $0 [sqlite|postgres] [pytest args...]" >&2
  echo "  sqlite   — file DB at repo root .pytest_local.sqlite3 (default)" >&2
  echo "  postgres — matches GitHub Actions (env DATABASE_* optional)" >&2
  exit 2
fi
if [[ $# -gt 0 ]]; then shift; fi

if [[ "$MODE" == "postgres" ]]; then
  export DATABASE_ENGINE=django.db.backends.postgresql
  export DATABASE_NAME="${DATABASE_NAME:-oscar}"
  export DATABASE_USER="${DATABASE_USER:-postgres}"
  export DATABASE_PASSWORD="${DATABASE_PASSWORD:-postgres}"
  export DATABASE_HOST="${DATABASE_HOST:-127.0.0.1}"
  export DATABASE_PORT="${DATABASE_PORT:-5432}"
else
  export DATABASE_ENGINE=django.db.backends.sqlite3
  export DATABASE_NAME="${ROOT}/.pytest_local.sqlite3"
  unset DATABASE_USER DATABASE_PASSWORD DATABASE_HOST DATABASE_PORT || true
fi

# Add sandbox to PYTHONPATH so that 'apps.storefront_settings' etc. can be found.
export PYTHONPATH="${PYTHONPATH:-}:${ROOT}/sandbox"

# Single process avoids SQLite locking; default collection path is tests/ when none is given
# (passing only pytest options like -k still targets tests/).
if [[ $# -eq 0 ]] || [[ "${1:-}" =~ ^- ]]; then
  set -- tests/ "$@"
fi
exec python -m pytest -n 0 "$@"
