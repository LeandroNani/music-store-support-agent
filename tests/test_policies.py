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

    # 7 and 10 are missing on purpose: they are the staff's own instructions.
    top_level = [n for n in numbers if "." not in n]
    assert top_level == ["1", "2", "3", "4", "5", "6", "8", "9"]

    assert "4.1" in numbers
    assert "8.3" in numbers

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


def test_the_internal_sections_are_out_of_reach():
    """The manual says "uso restrito da equipe de atendimento".

    Section 7 trains the human staff on how to talk to customers, and section 10
    tells them when to escalate to management. Neither is information for a
    customer, so the tool cannot return them and the index does not list them.
    """
    numbers = [section.number for section in list_sections()]

    assert "7" not in numbers
    assert "7.1" not in numbers
    assert "10" not in numbers

    for internal in ("7", "7.1", "7.2", "7.3", "10"):
        with pytest.raises(PolicySectionNotFound):
            get_section(internal)


def test_blocking_section_seven_does_not_break_the_rest():
    """Section 6 and section 8 still come back whole."""
    assert "não são cumulativas" in get_section("6").text
    assert "90 (noventa) dias" in get_section("8").text
