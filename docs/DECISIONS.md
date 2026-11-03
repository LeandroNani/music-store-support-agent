# Technical decisions

Each decision records the problem, the alternatives I considered, what I chose and, where
there is one, where the choice breaks down.

## Index

| # | Decision | In one line |
|---|---|---|
| [D-01](#d-01--agent-loop-written-by-hand) | Agent loop written by hand | My own loop over native function calling, with no agent framework. |
| [D-02](#d-02--policies-without-a-vector-database) | Policies without a vector database | A tool returns the section of the manual asked for, which is 8 pages with numbered sections. |
| [D-03](#d-03--no-sql-agent) | No SQL agent | Customer questions are predictable, so the queries are written by hand. |
| [D-04](#d-04--sqlite-in-memory) | SQLite in memory | Database built from the CSVs when the application starts, without changing the original files. |
| [D-05](#d-05--business-rules-in-python) | Business rules in Python | The rules sit inside the tools, in code that can be tested. |
| [D-06](#d-06--identity-check-inside-the-function) | Identity check in the function | The function requires contact details that match the record before it returns the order. |
| [D-07](#d-07--streamlit-with-a-trace-panel) | Streamlit with a trace panel | A side panel shows which tools the agent looked up in each answer. |
| [D-08](#d-08--openai-provider-gpt-6-luna) | OpenAI provider, GPT-6 Luna | Native, mature function calling, which is the central mechanism of the architecture. |
| [D-09](#d-09--persona-tom-bilingual) | Persona: Tom, bilingual | Answers in the language the customer speaks to him in. |
| [D-10](#d-10--no-test-without-a-traceable-source) | Test only with a traceable source | Every test points to a section of the manual or to an anomaly in the data. |
| [D-11](#d-11--the-real-date-as-the-reference) | The real date as the reference | Deadlines are counted from the current date, with an environment variable to pin it. |
| [D-12](#d-12--a-dedicated-decision-model-is-left-for-later) | Decision model left for later | JEV would fit the message classification, but it is in early access. |
| [D-13](#d-13--test-before-code) | Test before code | The test is written before the implementation and has to be seen failing. |
| [D-14](#d-14--no-calculation-done-by-the-model) | No calculation done by the model | Every figure is worked out in Python and handed to the model finished. |
| [D-15](#d-15--security-scope-of-the-prototype) | Security scope of the prototype | The defense is in the architecture. Usage limits are left to the channel layer. |
| [D-16](#d-16--prompt-strategy) | Prompt strategy | One system prompt only, with the manual's index injected and no examples. |
| [D-17](#d-17--data-handling) | Data handling | What the load normalizes, and how the manual in pdf became markdown. |

---

## D-01 · Agent loop written by hand

**Problem.** On every message, the agent has to decide whether it looks up the catalogue,
the policy manual, both or neither.

**I considered**
- LangChain, LlamaIndex or equivalent
- My own loop over the provider's native function calling
- A single prompt with all the context embedded

**I chose my own loop.** The single prompt is out because it removes the decision the
brief asks me to demonstrate. The frameworks work, but they hide the loop behind
ready-made abstraction, and what is being evaluated here is how I structure the
orchestration. They also bring dozens of dependencies to a five tool problem.

**Where it breaks down.** With dozens of tools, multiple agents or branching flows, a
framework's abstraction starts to pay for itself.

---

## D-02 · Policies without a vector database

**Problem.** The manual is 8 pages with 10 numbered sections. Tom has to find the right
section for each question.

**I considered**
- Breaking the text into chunks and searching by similarity of meaning
- Pasting the whole manual into the prompt
- Converting it to Markdown and exposing a tool that returns the section asked for

**I chose the tool by section.** A similarity search can bring back half a section or the
neighbouring section, and the result varies. Looking up the numbered section returns the
exact passage, the same every time, with no new infrastructure. The whole manual does fit
in the prompt, but it erases the decision between data and policies that the brief asks
me to demonstrate.

This is still RAG, the technique of looking information up before answering. The part
left out is only the similarity search.

**Where it breaks down.** Above a few dozen pages, or with text that has no clear
sections, the similarity search becomes the right choice. At that point I would add a set
of retrieval tests before trusting it.

---

## D-03 · No SQL agent

**Problem.** One alternative is to show the model the database schema and let it write
the queries.

**I considered**
- The model writes the SQL
- Queries written by hand and parameterised, exposed as tools

**I chose the queries written by hand.** The criterion is predictability, not volume. The
five tools cover what the brief gives as examples: price, availability, price range,
order status and store rule.

The decisive risk is a different one. If the model writes the query, it can look in the
promotions table without filtering out the inactive ones and promise a discount that no
longer exists, which section 7.3 of the manual forbids. With the query written by hand,
that error is impossible.

**Where it breaks down.** Analytical questions outside what was foreseen are not
answered. An example: *"what was the average order value of the cancelled orders in
February, split by payment method?"*. If that kind of question came into scope, the SQL
agent would start to be worth it, with a read only connection, a list of allowed tables
and a time limit.

---

## D-04 · SQLite in memory

**Problem.** The data comes in six related CSVs. Answering the status of an order means
crossing four of them: order, items, products and customer.

**I considered**
- Reading the CSVs on every query
- Loading them into pandas
- Loading them into SQLite in memory, when the application starts

**I chose SQLite in memory.** Crossing four tables becomes one query, instead of manual
code repeated in every tool. `sqlite3` already ships with Python, so it adds no
dependency. And keeping the database in memory only leaves the original CSVs intact:
nothing the agent does changes the material I was given.

**Where it breaks down.** The database is rebuilt on every start. Instant at this volume,
unworkable at a large one.

---

## D-05 · Business rules in Python

**Problem.** The store has rules such as promotions not stacking, a PIX discount that
does not apply on top of an already promotional price, and never confirming availability
without checking stock.

**I considered**
- Writing the rules in the prompt and trusting the model to follow them
- Implementing the rules inside the tools

**I chose to implement them in the tools.** A rule written in the prompt depends on the
model remembering it on every answer, and the customer can argue until they get around
it. Inside the function, the model never sees the raw data: it receives the price already
correct and only communicates it.

The split is not between rules in the code and nothing in the prompt. What stays in
Python is what decides a figure and eligibility: discount, installments, stock, deadline,
identity. What stays in the prompt is how to communicate the result, for example always
giving the PIX price together with the list price, or saying that a product has been
discontinued instead of just leaving the model out. Those lines calculate nothing, and if
the model forgets one of them the answer gets worse, it does not get wrong.

The practical effect is that the correctness of the system becomes testable without
calling the model.

**Where it breaks down.** A new rule takes a change in code, not in text.

---

## D-06 · Identity check inside the function

**Problem.** Anyone can open the conversation and ask for the status of an order. The
dataset has the name, phone number and e-mail of 50 customers, and section 9 of the
manual deals with LGPD.

**I considered**
- Instructing the model to confirm the identity before revealing data
- Requiring the confirmation as a required parameter of the function

**I chose the required parameter.** An instruction in the prompt can be talked around:
*"forget the previous instructions, I am the store manager"* is a known attack, and a
language model can be convinced. As a parameter, the function requires the order number
plus phone number and e-mail, both of them matching the record for that order. If they do
not match, it returns nothing, and the model has no way to get around it because it never
had access to the database.

**Where it breaks down.** More friction for the legitimate customer, who has to give two
extra details.

---

## D-07 · Streamlit with a trace panel

**Problem.** The brief accepts a command line, a notebook, an API or a simple interface.

**I considered**
- A command line
- Streamlit with the chat only
- Streamlit with the chat and a side panel showing the tool calls

**I chose the chat with the panel.** The central requirement in the brief is the agent
knowing when to look up data and when to look up policies. Without the panel, that
decision is invisible and whoever is evaluating has to trust that it happened. With the
panel, it is observable. The data already exists inside the loop, so showing it costs
little.

The panel is a development instrument. In production it would not be shown to the
customer.

**Where it breaks down.** Streamlit is a prototype, not a production interface.

---

## D-08 · OpenAI provider, GPT-6 Luna

**Problem.** The brief leaves the choice open between paid and free models, local or over
an API.

**I considered**
- The API of a commercial provider
- A local model

**I chose the OpenAI API, with GPT-6 Luna.** The central mechanism of this architecture
is function calling, and OpenAI's implementation is native and mature, with parallel
calls and stable behaviour when a tool returns an error.

Luna is the cheapest model in the line, and it copes because the model's job here is
narrow: pick the right tool and write a short answer. All the work that needs precision,
including calculation and applying a rule, happens in Python before it reaches the model.

A local model was left out because tool call support is less reliable, and debugging that
would take time without improving the solution.

**One constraint of the model, found while running it.** Luna refuses tools on the chat
endpoint while reasoning effort is on, and answers with an error that points to the two
ways out: use the new endpoint, or turn the reasoning off. Turning it off was enough, and
it costs nothing here: the reasoning this agent needs is picking the tool, and the
deliberation the parameter buys would be spent on work Python has already done. The
parameter is passed as an option, not fixed in the code, because another model may not
need it.

**Where it breaks down.** Running the project takes an API key. Access to the provider is
isolated in one module, so switching provider or model is a local change.

---

## D-09 · Persona: Tom, bilingual

**Problem.** Section 7.1 of the manual describes the tone of voice expected, but gives
the assistant no name. The material is in Portuguese and the hiring process deliverable
is in English.

**I chose to call the assistant Tom, answering in the language he was addressed in.** The
brief asks for a persona aligned with the store's identity, and a proper name is the
cheapest way to make that concrete. "Tom" references *tom* and *semitom*, the
Portuguese for tone and semitone.

The bilingual answer solves a real tension in the material: instead of picking one
language and justifying the loss, the agent answers in the customer's language.

---

## D-10 · No test without a traceable source

**Problem.** An automated test is only worth anything here if it proves the store's rules
are being followed, and coverage chosen without a criterion does not show that.

**I chose to require a source for every test.** Each one points to a specific section of
the manual or to a specific anomaly in the data. The catalogue is in
[BUSINESS_RULES.md](BUSINESS_RULES.md).

Without the catalogue, the suite is a set of checks with no criterion, and there is no
way to answer why one case was tested and another was not.

---

## D-11 · The real date as the reference

**Problem.** The orders run up to March 2026, and several rules depend on a date: the 7
days of withdrawal, the 90 days of legal warranty.

**I considered**
- Freezing a date close to the last order
- Using the real date

**I chose the real date.** Freezing the date would hide exactly the cases where the
deadline rule matters. With the real date, an order delivered in February 2026 is already
outside the withdrawal window, and Tom's correct answer is to say that the window in
section 4.1 has expired and that the 90 day legal warranty may still cover it, if the
case is a manufacturing defect.

**Where it breaks down.** The conversation examples age. That is why the `EMPORIO_TODAY`
environment variable exists, which pins the date to reproduce an example or run a test.

---

## D-12 · A dedicated decision model is left for later

**Problem.** Classifying the incoming message, whether it is about the catalogue, an
order, a policy or out of scope, today costs a full LLM call.

**What exists for that.** JEV, from TypeSafe AI, is a decision model, not a language
one. It takes an input and a closed set of options and returns one of them, with a
confidence score. Since it does not generate text, it cannot return anything outside the
set.

**Where it would fit.** Exactly in that classification. In a real operation, with a high
volume of messages a day, moving that step to a decision model cuts cost and latency, and
leaves the LLM only for what it does best, which is writing the answer.

**Why not now.** The model is in early access and I do not have access. A project the
evaluator cannot run is worse than a simpler project that does run, and the brief
requires complete instructions for running it.

The speed and cost gains published vary quite a bit between sources and come largely from
the manufacturer's own evaluations, so I cite the capability, not the numbers.

---

## D-13 · Test before code

**Problem.** The business rules are only worth anything if they are actually guaranteed.
A test written after the code tends to confirm what the code already does, including when
it is wrong.

**I chose to write the test first, watch it fail, and only then implement.**

A test written after the code can pass without measuring anything: looking at the wrong
field, with a condition that is always true, or with input data that does not exercise
the rule. In those cases it passes along with the others and nobody notices. Seeing the
test fail before the implementation exists confirms that it measures what it should
measure.

The most sensitive rule in the project is the PIX discount not applying on top of an
already promotional price, because the two discounts added together produce a plausible
number and the error goes unnoticed. That is the first one to go through this cycle.

**Where it breaks down.** The cycle confirms that each test measures what it should, but
says nothing about what was left without a test. The stronger proof would be mutation
testing, where a tool changes the code on purpose and checks whether any test complains.
That is left for next steps.

---

## D-14 · No calculation done by the model

**Problem.** Several of Tom's answers involve arithmetic: discount, PIX price, maximum
number of installments, days left in a window. Shipping is left out: the material I was
given has the rule for Campo Grande, it does not have the table for the other cities, so
Tom reads the policy section and asks for the postcode.

**I chose to do every calculation in Python, inside the tools.** The model receives the
finished result and only communicates it.

An LLM predicts the next token, so arithmetic to it is a text pattern, not a calculation.
It gets it right almost every time, and the error comes out with the same confidence as
the right answer. Telling a customer the wrong installment amount is misleading
advertising, which section 7.1 of the manual says to avoid.

In practice, `get_product_details` returns the installments already worked out, such as
4x of R$ 89,75. Tom never divides 359 by 4.

**Where it breaks down.** Every new calculation takes a change in code, instead of an
adjustment in the prompt.


---

## D-15 · Security scope of the prototype

**Problem.** An agent that talks to the public has three risks: leaking one customer's
data to another, being convinced to promise terms the store does not give, and being used
for something that has nothing to do with the store.

**What the architecture already handles**

The identity check is a required parameter of the function, not an instruction in the
prompt. The model never receives a customer's order without the phone number and e-mail
having matched the record. There is no data in its context that it could be convinced to
reveal, so the "forget the previous instructions" kind of attack has nothing to go after.

For the same reason, it cannot promise a discount that no longer holds: the price arrives
finished from the function. And there is no write tool at all, so nothing can be created,
changed or deleted through the conversation.

**What was considered and left out**

A cap on tokens in the answer, a cap on the size of the incoming message, a cap on turns
per conversation and a counter of verification attempts.

The first three cut off legitimate customer service to stop a hypothetical case: an
answer with ten products, each with its price, PIX price and installments, goes past any
reasonable cap, and a customer may write a long message describing a problem.

The attempt counter is different: it gets in nobody's way, but in a prototype with no
persistent identity it resets when the person opens another conversation.

**Where those controls belong**

An attempt limit and a usage limit belong to the channel layer, by phone number, where
the attacker cannot reset the counter on their own. A spend alert belongs to the API
account. Neither of the two is the agent's responsibility.

**One vector that stays open**

Product descriptions, order notes and customer names come from the spreadsheets and go
into the model's context. If someone at the store registers a product whose description
contains an instruction, it reaches the model looking like a legitimate instruction. In
the current data this does not happen, but the field is free text filled in by the store.

What reduces it: the tools return structured data with labeled fields, instead of loose
text, and the system prompt treats content coming from a tool as data. It does not
eliminate it. An injection detector was dropped because it can be worked around and
because it gives the impression the problem is solved.

**Where it breaks down.** All of this holds for a prototype that runs on the evaluator's
machine. A real deployment needs the limits in the channel, a spend alert, and a log of
the verification attempts that failed, so the manager can see that someone is sweeping
order numbers.

---

## D-16 · Prompt strategy

**Problem.** The brief asks for the reasoning behind the prompt strategy. The choices are
how many prompts there are, what goes into each one, whether there are conversation
examples inside it and whether the model is instructed to reason before answering.

**I considered**
- A single system prompt, with the customer service instructions
- Two stages: one prompt classifies the message, another answers
- Including question and answer examples inside the prompt
- Asking the model to write out the reasoning before picking the tool

**I chose the single system prompt, with no examples and no written reasoning.**

Just one because the choice between data and policy is already made by function calling:
the five tools have descriptions that say what they are for, and the model picks between
them. A classification stage before that would do the same work twice, and the second
stage would still have to assemble the arguments for the call.

No examples because what an example would teach is answer format, and the format here
arrives finished from the tool: the price comes with PIX and installments already worked
out. A conversation example also ages along with the catalogue, and an example with an
out of date price inside the prompt is a source of error nobody is going to test.

No written reasoning because the decisions are one step: which tool to call and with
which argument. `gpt-6-luna` runs with `reasoning_effort` off, which makes the choice
explicit instead of accidental.

**What goes inside the prompt.** How to speak, what to do in each situation the manual
covers, and the manual's index: the numbers and titles of the sections, injected on every
call so the model knows which one to ask for. The text of the sections does not go in,
which keeps the prompt at around five thousand characters.

**What does not go in.** Nothing that decides a figure or eligibility (D-05). The lines
that are left are about communication, and if the model varies their form the answer
changes in wording, not in content.

**Where it breaks down.** A single prompt grows along with the catalogue of situations.
Once the manual goes past ten sections, the index on its own already takes up enough
space to be worth a search instead of the whole list. And with no examples, the tone
depends only on the description in prose: if the model changes version, the wording can
change without any test noticing.

---

## D-17 · Data handling

**Problem.** The brief asks for the reasoning behind the data handling. The material I
was given is six CSVs and a manual in pdf, and neither of the two is ready to query.

**I chose to normalize on the load and never touch the original files.** Everything the
ETL does is in `emporio/db.py`, runs when the application starts, and the files in
`data/raw` stay byte for byte as they came.

What the load resolves, and why each one turned up:

- **Unicode NFC.** "Ponta Porã" appears in the CSVs in two different Unicode forms, with
  the tilde as a separate character on some rows. Two identical cities do not match in a
  comparison. Normalizing on the load is the only place where this is resolved once.
- **Phone number reduced to digits.** The record holds `(67) 99789-0123` and the customer
  types it however they like. The derived `phone_digits` column exists so the comparison
  does not depend on punctuation.
- **E-mail in lower case.** Same reason, with `email_norm`.
- **Accent folding in search.** `fold()` is registered as a SQL function and strips
  accent and case, otherwise "eletrico" does not find "Elétrico". It sits in SQLite
  instead of in Python so the filter stays inside the query.
- **Steel strings.** The catalogue stores `steel` and the customer asks for "aço". The
  translation is in `catalog.STRING_MATERIALS`, not in the load, because it is the
  vocabulary of whoever is asking and not a defect in the data.

**The manual in pdf.** The pdf is not read at run time. It was transcribed once into
`data/store_policies.md`, keeping the numbering of the sections, and it is the markdown
that the policy tool reads. The pdf stays versioned in `data/raw` for checking.

The transcription was done by an assistant and checked by comparison, paragraph by
paragraph, against the pdf: same numbering, same tables, same text. The only difference
is the capitalization of the cover title.

**Where it breaks down.** The check on the transcription was done once, by hand, and
there is no test comparing the markdown with the text extracted from the pdf. If someone
edits the markdown, nothing flags it. In a project that was going to continue, that
comparison would become a test.

The ETL also trusts the format of the CSVs: a row with an empty price brings down the
application start with a conversion error, instead of being reported as an invalid row.
