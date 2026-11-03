# Assumptions

The brief asks for ambiguities to be resolved with a reasonable interpretation and
documented. This document records the ambiguities in the **brief**, and what was assumed
in each one.

The ambiguities in the **data**, which turn into code and tests, are in
[BUSINESS_RULES.md](BUSINESS_RULES.md).

---

## S-01 · The channel is WhatsApp, but with no integration

**The ambiguity.** The manual treats WhatsApp as the main remote customer service
channel. The brief does not ask for integration with anything.

**Assumed:** WhatsApp is the channel in the story, not a technical requirement. The brief
accepts a command line, a notebook, an API or a simple interface, which confirms that the
integration is not expected. What WhatsApp does define is the **tone**: a short, informal
message, the way someone answers on a phone.

That has a security consequence. On real WhatsApp, the phone number of whoever is talking
arrives verified by the channel itself, without the customer having to type it. Here that
data does not exist, so when the customer asks for order information Tom has to ask for a
phone number and an e-mail, and trust what was typed. It is a weaker check than it would
be in production, and it is recorded as a known limitation.

---

## S-02 · Language

**The ambiguity.** The process e-mail requires every answer to be in English. The brief,
the store's policy manual and the data are in Portuguese, and the store is in Campo
Grande.

**Assumed:** they are two different audiences. The repository documentation, which is the
deliverable being evaluated, goes in English. Tom answers in the language the customer
speaks to him in.

During development, the documentation is written in Portuguese and translated at the end.

---

## S-03 · The reference date

**The ambiguity.** The orders in the dataset run up to March 2026, and several rules
depend on a date: 7 days of withdrawal, 30 days of defect exchange, 90 days of legal
warranty. The brief does not say at what moment the system is running.

**Assumed:** the system's real date. The environment variable `EMPORIO_TODAY` makes it
possible to fix a date to reproduce an example or run a test.

The effect is that the withdrawal windows of the orders in the dataset have already
expired, and Tom's correct answer becomes more interesting: saying that the window has
closed and saying which rule may still apply, such as the 90 day legal warranty in case
of a defect.

---

## S-04 · Tom only reads, never writes

**The ambiguity.** Section 7.3 of the manual says to record complaints and pass them to
the person responsible. But the material received is read only: there is no ticketing
system, and the spreadsheets have nowhere to write anything.

**Assumed:** Tom has no write tool at all. He does not create an order, does not cancel
one, does not change a record and does not log a complaint anywhere. He looks things up,
answers and helps. Faced with a complaint, he takes it in, explains the procedure and
gives the 24 business hour response window the manual sets out.

Besides being what the data allows, it is the safer choice. An agent that talks to the
public and has permission to change data needs a level of control that is outside the
scope of a prototype.

---

## S-05 · Conversation history persistence

**The ambiguity.** The brief leaves it open, saying to implement it "if it makes sense for
the user experience".

**Assumed:** history within the session, yes. Without it Tom does not understand
*"and the cheapest of those?"*, which is a normal question from someone comparing
products. Between sessions, no: it would require identifying the customer in a persistent
way, which is the real channel's responsibility and not this prototype's.

---

## S-06 · Two delivery channels

**The ambiguity.** The brief says to reply to the e-mail with the repository link. The
process e-mail says to send a PDF through Google Forms.

**Assumed:** both. The PDF sent through the form holds the repository link and a summary
of the decisions, and the e-mail is answered with the same link.

---

## S-07 · What is expected of a prototype

**The ambiguity.** The brief asks for a prototype and says the focus is the agent working
correctly, without defining what is left out.

**Assumed:** what is left out is everything that is operations and not agent behavior.
No user authentication, no deploy, no container, no continuous integration, no server
database and no monitoring. What is in is the agent being correct, tested against the
rules that matter, and runnable on the evaluator's machine.

---

## S-08 · Who talks to Tom

**The ambiguity.** The brief says the agent is going to "help the team with customer
service". That has two readings: Tom answers the customer, or Tom is a lookup tool that
the staff member uses while talking to the customer. The two change everything: the
second needs no identity check at all, because whoever is asking is already from the
store.

**Assumed:** Tom talks to the customer. Section 7 of the manual already puts the virtual
assistant on the WhatsApp channel alongside the human staff, and the way it helps the
team is by absorbing the repeated questions before they reach a person.

The consequence is the identity check. If Tom talked to the team, asking for a phone
number and an e-mail to pull up an order would be pointless friction.
