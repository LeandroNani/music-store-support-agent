"""Policy manual, served one section at a time.

The manual is eight pages with ten numbered sections, so a section lookup
returns the exact text every time. Decision D-02 covers why there is no
embedding search here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

MANUAL_PATH = Path(__file__).resolve().parent.parent / "data" / "store_policies.md"

# "## 4. Política de Trocas e Devoluções" and "### 4.1 Direito de Arrependimento"
HEADING = re.compile(r"^(#{2,3})\s+(\d+(?:\.\d+)?)\.?\s+(.+)$")

# The manual's cover reads "Documento interno, uso restrito da equipe de
# atendimento". Most of it is customer facing anyway: opening hours, payment,
# returns, shipping, warranty. These two are not.
#
# Section 7 trains the human staff on tone of voice and the steps to follow,
# and section 10 tells them when to escalate to management. Read out to a
# customer, they expose how the store runs its service desk.
#
# The block is here rather than in the prompt for the same reason the identity
# check is a parameter: the agent cannot hand over text it was never given.
INTERNAL_SECTIONS = frozenset({"7", "7.1", "7.2", "7.3", "10"})


class PolicySectionNotFound(LookupError):
    """Raised instead of returning the nearest section."""


@dataclass(frozen=True)
class PolicySection:
    number: str
    title: str
    text: str


@lru_cache(maxsize=1)
def _parse_manual() -> dict[str, PolicySection]:
    lines = MANUAL_PATH.read_text(encoding="utf-8").splitlines()

    headings: list[tuple[int, int, str, str]] = []  # line, level, number, title
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match:
            level = len(match.group(1))
            headings.append((index, level, match.group(2), match.group(3).strip()))

    sections: dict[str, PolicySection] = {}
    for position, (start, level, number, title) in enumerate(headings):
        # A section runs until the next heading at the same level or above, so
        # asking for 4 brings 4.1 through 4.4 and asking for 4.1 does not.
        end = len(lines)
        for next_start, next_level, _, _ in headings[position + 1 :]:
            if next_level <= level:
                end = next_start
                break
        if number in INTERNAL_SECTIONS:
            continue
        text = "\n".join(lines[start:end]).strip()
        sections[number] = PolicySection(number=number, title=title, text=text)

    return sections


def list_sections() -> list[PolicySection]:
    """Index of the manual, for the system prompt. Text is omitted on purpose."""
    sections = _parse_manual().values()
    return sorted(
        (PolicySection(s.number, s.title, "") for s in sections),
        key=lambda s: [int(part) for part in s.number.split(".")],
    )


def get_section(number: str) -> PolicySection:
    sections = _parse_manual()
    key = number.strip().rstrip(".")
    if key not in sections:
        available = ", ".join(s.number for s in list_sections())
        raise PolicySectionNotFound(
            f"section {number} is not in the manual. Available: {available}"
        )
    return sections[key]
