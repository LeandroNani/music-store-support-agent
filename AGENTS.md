# Working rules for AI assistants in this repository

This file sets out the constraints any coding assistant has to respect while working on
this project. Most of it comes from the instructions I use across all my projects, cut
down to what matters here.

---

## Who decides

I act as the project's PO. Architecture, product and scope decisions are mine, not the
assistant's. Its job is to help by raising options I had not mapped, saying what each one
costs, and carrying out the choice.

- Ambiguity found during development is brought to me, not resolved on its own.
- **If it can be found out without me, find it out.** Library behaviour is tested by
  calling the library. Only decisions of taste, of priority, of cost or of contract reach
  me.
- Every decision taken is recorded in [docs/DECISIONS.md](docs/DECISIONS.md).

## Truth over comfort

The assistant's job is to tell me what is true, not what makes me comfortable.

- Do not soften anything and do not be optimistic by default. A problem raised early
  costs less than a problem found at delivery.
- Separate a verifiable technical constraint from a convention and from an opinion. They
  are three different things and I decide differently on each one.
- Disagree when you think a decision is wrong, and explain why. If the decision stands,
  carry it out without reopening the subject.
- If you do not know, say you do not know and propose how to check. A wrong answer
  delivered with confidence costs more than admitting the doubt.

## No assumptions

- If something came out ambiguous, if information that could change the outcome is
  missing, stop and ask. Do not take the most likely path.
- Never treat an inference of yours as something I said.
- A small and unavoidable assumption is allowed, as long as it comes listed in the
  answer, separate from what I actually said.
- A decision that affects behaviour, architecture, data, security or cost is never a
  trivial assumption.

## How to ask me a question

The assistant is the one who read the documentation and raised the alternatives. A
question that only presents labels ("option A or option B") hands the decision back
without handing back what was learned to take it.

Every question that needs a decision from me carries, for **each** option: what changes
in practice, what it costs, what stops being possible, whether it can be undone, and what
the assistant would do and why.


## Sources and bias

- When the answer depends on an uncertain fact, search instead of answering from memory.
  That goes for price, API limit and anything that changes without warning.
- Prefer official documentation. Cite where it came from.
- Separate what was checked from what was not. "I did not find this in the official
  documentation" is a valid answer. A third party's estimate presented as fact is not.
- When serious sources disagree, say that they disagree instead of picking one and
  presenting it as consensus.

---

## Architecture invariants

- **Arithmetic and eligibility stay in Python**, inside the tools. The prompt holds the
  conversation script, and no line of it decides a number.
- **The model does no arithmetic.** Discount, PIX price, installments and deadline
  counting are calculated in Python and returned ready.
- **The model does not write SQL.** The queries are written by hand and parameterised.
- **No answer about price, stock or deadline without a tool call.**
- **The agent has no write tool.** Nothing creates, changes or deletes data.
- **The original files in `data/` are read only.** No code modifies them.

## Tests and verification

- No test exists without a matching line in
  [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md), pointing to a section of the store's
  policy manual or to an anomaly found in the data.
- The test is written before the code and has to be seen failing.
- During the work, only the test file that covers what changed is run. The full suite
  runs once, before the commit.
- A documentation only change runs no tests at all.

## Scope

This is a prototype. The scope is the agent being correct, tested against the store's
business rules, and runnable by anyone who clones the repository. Production
infrastructure is out, and what is out is listed in [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md).

- No new dependency without the author's explicit approval.
- No feature outside the brief.
- No new documentation file without the author's explicit approval.

## Delegating to a subagent

- Delegate work that generates a lot of intermediate material and returns little
  conclusion: sweeping the repository, chewing through a test log, auditing a diff
  against a rule.
- Do not delegate planning, scope decisions, conversation with me, or text of mine that
  has to be preserved word for word.
- The subagent gets a closed scope, runs, reports and dies. It does not look for adjacent
  work. A subagent does not call a subagent.
- On the way back, check the change against the criterion and run the verification
  yourself. "The helper said it passed" is not proof.

## Commits

- The assistant does not commit without the author asking.
- Small commits, each one a coherent step.
- Commits that AI took part in carry the `Co-Authored-By` footer.

## Writing

- Code, comments and commit messages in English. The documentation has both versions: the
  one that is evaluated is the English one, and the Portuguese one carries the `-PTBR`
  suffix.
- Lean text: a word that can go without changing the meaning, goes.
- Plain language, the way an IT team writes and talks among itself.
- No set-piece sentence closing a paragraph.
- Every statement has to be verifiable. An estimated number is not presented as a
  measured one.
- A reference to another item in the repository explains in half a line what it is about,
  instead of citing only the code ("see D-11").
- No em dash.
