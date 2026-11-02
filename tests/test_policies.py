"""Policy manual retrieval.

The manual is returned one section at a time, by number. See decision D-02 for
why there is no similarity search here.
"""

import pytest

from emporio.policies import PolicySectionNotFound, get_section, list_sections


def test_index_lists_every_section_and_subsection():
    """The index goes into the system prompt so the agent knows what it can ask for.

    Subsections are listed too: for "can I return this?" the agent should be able
    to ask for 4.1 instead of pulling the whole returns policy.
    """
    sections = list_sections()
    numbers = [section.number for section in sections]

    top_level = [n for n in numbers if "." not in n]
    assert top_level == ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

    assert "4.1" in numbers
    assert "7.3" in numbers

    titles = {s.number: s.title for s in sections}
    assert titles["2"] == "Horário de Funcionamento"


def test_section_includes_its_subsections():
    """Asking for 4 returns the whole returns policy, 4.1 through 4.4."""
    section = get_section("4")

    assert "7 (sete) dias corridos" in section.text  # 4.1
    assert "30 (trinta) dias corridos" in section.text  # 4.2
    assert "Boquilhas de instrumentos de sopro" in section.text  # 4.4


def test_subsection_returns_only_itself():
    """Asking for 4.1 must not drag in the neighbouring subsection."""
    section = get_section("4.1")

    assert "7 (sete) dias corridos" in section.text
    assert "Trocas por Defeito" not in section.text


def test_unknown_section_is_reported_not_invented():
    """A wrong section number fails loudly instead of returning the closest one."""
    with pytest.raises(PolicySectionNotFound):
        get_section("12.5")
