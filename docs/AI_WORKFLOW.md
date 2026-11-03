# Use of an AI assistant

## Tool

Claude Code, running in Anthropic's desktop application.

## How the work was run

The architecture, product and scope decisions are mine. The assistant lays out the
options and says what each one costs, I choose, and it carries out the choice.

The order was documentation before code. Before any implementation existed, I settled
the approach, recorded the decisions in [DECISIONS.md](DECISIONS.md) and built the
catalogue of rules in [BUSINESS_RULES.md](BUSINESS_RULES.md). That catalogue is the
specification the tests were written against.

The constraints I put on the assistant are in [AGENTS.md](../AGENTS.md), inside the
repository. They cover architecture, scope, tests, commits and writing style, and they
hold for any assistant working on this project.

## What was delegated and what was not

**Delegated:** drafting, implementing the tools, building the in-memory database from
the CSVs, writing the tests from the catalogue of rules, and the interface.

**Not delegated:** the choice of approach, where the scope was cut, the decision on
each conflict between the manual and the data, Tom's persona, and the final text of the
documentation.

The documents in this repository started as drafts by the assistant. I changed, added,
corrected and edited what needed it, and checked the rest.

## Commits

Commits the assistant took part in carry the `Co-Authored-By` footer. The history shows
the real progress of the work, with no history rewriting.
