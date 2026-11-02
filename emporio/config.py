"""Environment and the reference date.

Reads .env.local first, then .env, and never overrides a variable already set
in the shell. Both files are gitignored; .env.example is the committed template.

Written by hand instead of pulling in a dependency: it is a dozen lines and the
project has no other use for one.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILES = (".env.local", ".env")

# Decision D-11: the agent works off today's real date. This variable pins it so
# an example conversation or a test can be reproduced later.
DATE_OVERRIDE = "EMPORIO_TODAY"


def load_env() -> None:
    for name in ENV_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def api_key() -> str:
    load_env()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return key


def model_name() -> str:
    load_env()
    return os.environ.get("OPENAI_MODEL", "gpt-6-luna").strip()


def today() -> date:
    """The date every deadline is counted from."""
    load_env()
    pinned = os.environ.get(DATE_OVERRIDE, "").strip()
    return date.fromisoformat(pinned) if pinned else date.today()
