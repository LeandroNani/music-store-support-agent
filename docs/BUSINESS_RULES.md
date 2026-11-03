# Catalogue of business rules

The store's manual is a pdf written for the team to read. The data sits in six
spreadsheets. For Tom to work, every rule in the manual had to become code, and in
several places the manual contradicts the data.

This document is that work: what the manual requires, what the data shows, and what was
decided where the two disagree. No test in this repository exists without a line here.

- [Part A: rules taken straight from the manual](#part-a--rules-taken-straight-from-the-manual)
- [Part B: conflicts between the manual and the data](#part-b--conflicts-between-the-manual-and-the-data)
- [Part C: traceability matrix](#part-c--traceability-matrix)

---

## Part A · Rules taken straight from the manual

Rules where the manual is clear and the data does not contradict it. They go into the
code without any further decision.

### Price and payment

| Rule | Source |
|---|---|
| PIX gives 5% off the list price | section 3 |
| The PIX discount does not apply on top of a promotional price | section 6.2 |
| Promotions do not stack with each other | section 6.2 |
| A promotional price is always shown with the original price and the percentage | section 6.2 |
| Credit up to 3x: minimum installment of R$ 50,00 | section 3.1 |
| Credit from 4x to 6x: minimum installment of R$ 80,00 | section 3.1 |
| Credit from 7x to 12x: minimum installment of R$ 100,00 | section 3.1 |
| Combining payment methods: only above R$ 2.000,00 | section 3.1 |
| Bank slips clear within 3 business days | section 3 |

> **Consequence in the code:** the maximum number of installments depends on the price.
> A product at R$ 359,00 takes up to 4x (R$ 89,75, above the R$ 80,00 minimum), but it
> does not take 5x (R$ 71,80), nor anything in the 7x to 12x band.
>
> No arithmetic is done by the agent (D-14, which explains why). The function returns
> the installments already resolved and Tom communicates them. The same holds for the
> discount, the PIX price and counting deadlines. Shipping is not included: the material
> received gives no table for it.

### Exchanges, returns and warranty

| Rule | Source |
|---|---|
| Withdrawal: 7 calendar days after receipt, no reason needed | section 4.1 |
| Withdrawal requires the original packaging, unused, with accessories and manuals | section 4.1 |
| Refund through the same payment method, within 10 business days | section 4.1 |
| The store pays the return shipping in a withdrawal | section 4.1 |
| Manufacturing defect: exchange within 30 calendar days of the purchase | section 4.2 |
| After 30 days the warranty goes to the manufacturer; the store can act as go-between | section 4.2 |
| Exchange by preference: 7 days, subject to the wanted product being available | section 4.3 |
| Not exchangeable: custom items, clearance marked as final sale, mouthpieces | section 4.4 |
| Legal warranty: 90 days against defects, counted from receipt | section 8.1 |
| Manufacturer's warranty: varies from 6 months to 2 years | section 8.2 |
| The warranty does not cover wear, misuse, third-party repair or cosmetic damage | section 8.3 |

### Shipping

| Rule | Source |
|---|---|
| Campo Grande and around it: free shipping above R$ 500,00 | section 5.1 |
| Campo Grande and around it: below R$ 500,00, a flat R$ 35,00 | section 5.1 |
| Campo Grande and around it: delivery in 1 to 3 business days, by the store's own courier | section 5.1 |
| Other cities: PAC 5 to 12 business days, SEDEX 2 to 5, Jadlog 3 to 8 | section 5.2 |
| Every shipment includes insurance | section 5.2 |
| Large instruments may need an individual shipping quote | section 5.2 |
| Tracking code: BR + 9 characters + BR, sent when the order is dispatched | section 5.3 |

> **Consequence in the code:** the free shipping rule only holds for Campo Grande. The
> customers in the dataset are spread across five cities, and 26 of them are outside
> Campo Grande.

### Customer service and scope

| Rule | Source |
|---|---|
| Informal but professional tone of voice, no robotic language | section 7.1 |
| Never state a price, stock level or deadline without checking the system | section 7.1 |
| The store sells instruments only, it does not sell accessories | section 1, section 7.1 |
| Accessories named: strings, picks, cables, cases, pedals, amplifiers | section 1 |
| A request for an accessory is redirected politely, suggesting a partner store | section 7.1 |
| Product out of stock: say so and suggest similar alternatives | section 7.3 |
| Discontinued product: say so and offer an equivalent or a successor | section 7.3 |
| Promotion over: say so plainly and give the current price | section 7.3 |
| Never promise a discount that is no longer running | section 7.3 |
| Complaint: listen with empathy, record it, pass it on. Reply within 24 business hours | section 7.3 |
| Hours: Mon to Fri 9am to 6pm, Saturday 9am to 1pm, closed Sunday and holidays | section 2 |
| Outside business hours, state when the store is back | section 7.1 |

### Personal data

| Rule | Source |
|---|---|
| Customer data is used only for the order, tracking, promotions and legal duties | section 9 |
| Data is not shared with third parties for marketing | section 9 |

---

## Part B · Conflicts between the manual and the data

Here the material received gives no answer. Each item is a decision taken.

### B-01 · Discontinued product with stock on the shelf

Product 136 (Ibanez Bass 2X, R$ 441,00) is flagged `discontinued` and has **13 units in
stock**. The manual says to tell the customer a discontinued product has left the
catalogue and to offer an equivalent, but it did not allow for there still being units
on the shelf.

**Decided:** it does not come up in a search, because it is no longer part of the
catalogue the store offers. But if the customer asks for it by name, Tom offers it and
says it is a discontinued line. That follows the manual without throwing away stock that
exists and that the store wants to sell.

---

### B-02 · A product not yet launched that has already been sold

Product 130 (Kala KA-ABP-CTG Barítono) is flagged `coming_soon` with 2 units, but it
shows up in two orders already placed: order 3, delivered in December 2025, and order
14, pending.

**Decided:** Tom does not sell it and says it is not on sale yet. The status is the field
the system exposes, and Tom should not infer that a record is wrong just because the
history disagrees with it.

The inconsistency is the store's own data problem. In a future step, the admin panel
lists the inconsistencies for the manager to fix at the source.

---

### B-03 · Active product with no stock and promotions switched off

Product 96 (Giannini GF-3D, R$ 799,90) is `active` with **zero** stock, carries two
promotions (18% and 40%), **both switched off** (`is_active = 0`), and has already been
sold in order 4. The manual talks about a promotion being over; the spreadsheet can only
say on or off, with no date, so off is what the code applies.

**Decided:** the search returns every product that matches what the customer asked for,
each one marked **In stock** or **Out of stock**. The product is part of the catalogue
and is only missing units right now, so the customer needs to know it exists. Tom
suggests an alternative for whatever has run out, as section 7.3 requires.

Neither promotion can be mentioned, because both are switched off.

---

### B-04 · The order total does not match the sum of its items

In 2 of the 20 orders, the stored total differs from the sum of the item prices:

| Order | Stored total | Sum of items | Difference |
|---|---|---|---|
| 3 | R$ 3.450,00 | R$ 3.498,00 | R$ 48,00 |
| 20 | R$ 1.400,00 | R$ 1.488,00 | R$ 88,00 |

**Decided:** the stored total is the truth and Tom never recalculates. That is the
amount that went through the payment method, and the difference is probably a discount
given at the till and not recorded per item. Recalculating would have Tom state an
amount the customer never paid.

The divergence is the store's own data problem. In a future step, the admin panel shows
these orders for the manager to decide what to do at the source.

---

### B-05 · Categories that exist with no product in them

The catalogue has 9 categories. Three are empty: Instrumentos de Sopro (Madeiras),
Instrumentos de Sopro (Metais) and Cordas Orquestrais. If a customer asks for a
saxophone or a violin, the category exists but there is nothing to sell.

**Decided:** Tom answers that the store works with the category and has no units
available at the moment. Section 1 of the manual lists wind and orchestral strings among
what the store sells, so this is lack of stock and not lack of scope. The customer
learns they can come back.

---

### B-06 · Which source wins when the manual and the data disagree

Section 1 states that the catalogue holds more than 300 instruments. The product
spreadsheet holds 65.

The number itself is not the problem: the manual may be out of date, and the customer is
not going to check. The problem is Tom stating anything about availability from the
manual instead of from the data. If he says "we have more than 300 instruments,
including wind" and then cannot name a single saxophone in the next answer, he
contradicts himself inside one conversation.

**Decided:** verifiable data (product, price, stock, size of the catalogue) comes from
the spreadsheet. Rules (exchanges, shipping, payment, warranty, tone of voice) come from
the manual. Tom does not state a total number of products, because there is no reliable
source for that number. Section 7.1 already points that way, by forbidding him to state
stock without checking the system.

Section 1 of the manual reaches the model whole, with the "more than 300" inside it, so
the decision has to live in the prompt: it tells him to take product figures from the
tool and not to repeat the manual's. That is a rule about communicating, not about
arithmetic, which is why it belongs there.

---

### B-07 · Two different phone numbers in the same manual

Section 1.2 gives the phone number (67) 3341-4444. Section 7 says the WhatsApp channel
is (67) 3321-4500. The e-mail also appears in two forms, one of them with an accent in
the domain.

**Decided:** both numbers stay, and Tom gives whichever fits the question. Section 1.2
labels 3341-4444 as "Telefone / WhatsApp" and section 7 gives a different number for
WhatsApp, so it is a genuine contradiction, not a landline and a text line. For a
question about service over messaging, section 7's number wins, because that is the
section covering it.

Of the two e-mail forms, only the one without the accent is a valid address. The
accented form sits in the table in section 1.2, which Tom can read, so the correction is
in the prompt alongside the one about product figures.

---

### B-08 · How the price is presented

The customer asks what the Takamine GD20 costs. Is the answer R$ 2.199,00, or
R$ 2.199,00 and R$ 2.089,05 on PIX? Section 6.2 requires a promotional price to appear
with the original price and the percentage, but it does not say whether the PIX discount
should be mentioned without the customer asking.

**Decided:** Tom always shows both, the list price and the PIX price. The manual wants
full transparency on price, and stating the better terms is better service.

When there is an active promotion, the answer shows the original price, the percentage
and the final price, and makes it explicit that the PIX discount does **not** add to the
promotional price.

> This rule is hard to catch in a review, because the two discounts added together give
> a number that looks right. That is why the test proving that PIX does not apply on top
> of a promotional price is written before the pricing code exists, and has to be seen
> failing first.

---

### B-09 · What goes into a search by price range

The brief suggests the case *"quais opções de violões disponíveis custando até
R$ 1.000?"*. Does the price filter use the list price or the price with the promotion?
And what happens to a discontinued product and to one that has run out?

**Decided:** the filter uses the lowest price the customer can actually pay, which means
the price with the active promotion and also the PIX price. The Giannini GNF-3 costs
R$ 1.049,00 and comes to R$ 996,55 on PIX, so it goes into a search for "up to R$ 1.000"
with a note that it only fits the budget on PIX. Hiding it would be worse service,
because the product does fit and it only depends on the payment method.

A product with no stock appears in the list, marked **Out of stock**. A discontinued
product stays out of the search, and is only offered if the customer asks for it by
name.

---

### B-10 · What Tom asks for before releasing order information

The architecture decision was to make the identity check a required parameter of the
function rather than an instruction in the prompt. What was left was deciding which
detail. Each customer has a name, a phone number, an e-mail and a city. There is no
national ID and no password.

**How it would work in production.** On WhatsApp, the phone number of whoever is writing
already comes from the channel, verified, without the customer having to state it. The
number would not be asked for, it would be read from the connection, and Tom would ask
only for the e-mail as a second factor. If the person gave a phone number different from
the connected one, there would be no authorization.

**Decided:** since this prototype has no WhatsApp integration, nothing arrives verified.
So Tom asks for **the phone number and the e-mail**, and both have to match the record
on that order. Asking for both makes up, in part, for the missing factor the channel
would give.

**Limitation:** a phone number typed by the customer is not a verified phone number. In
a real deployment the number would come from the WhatsApp session and this check would
start to mean something.

### B-11 · Which date the deadlines are counted from

The manual counts withdrawal and the legal warranty "from receipt of the product". The
order spreadsheet has no receipt date: it has `order_date`, which is the purchase date,
and `estimated_delivery`, which is the expected delivery.

**Decided:** use `estimated_delivery` as the receipt date, and only for orders with
status `delivered`. It is the closest field to what the manual asks for, and for an
order already delivered the estimate has passed. The defect exchange, which the manual
counts from the purchase and not from receipt, uses `order_date`.

An order not yet delivered has no withdrawal and no warranty window counted, because
nothing was received.

**Limitation:** an expected delivery is not a delivery. An order that ran late has the
wrong date, and wrong on the short side, which cuts the customer's window. In a real
deployment the receipt field would come from the carrier.

---

### B-12 · Defect exchange on an order the customer never received

Section 4.2 gives 30 calendar days **after the purchase** to exchange a product with a
manufacturing defect. The deadline counts from the purchase, not from receipt, and it is
the only one of the three that does.

Reading the text literally, order 20, which was cancelled over an invalid address, would
have until 2026-04-07 to exchange for a defect. The same holds for a pending order and
for one still on its way.

**Decided:** the window is only reported for a delivered order. The rule exists to
exchange a faulty product, and a cancelled order never put any product in the customer's
hands. The start date is still the purchase date, as the manual requires.

Telling a customer whose order was cancelled that they can still exchange the product
until a given date is worse than saying nothing: they will hold the store to it.

---

### B-13 · The manual gives two different minimum installments

The table in section 3 says "Cartão de Crédito | Até 12x sem juros | Parcela mínima de
R$ 100,00". Section 3.1 gives bands: R$ 50,00 up to 3x, R$ 80,00 from 4x to 6x,
R$ 100,00 from 7x to 12x. On the first reading, the Yamaha C40 at R$ 599,90 goes up to
5x. On the second, 6x of R$ 99,98.

**Decided:** the bands in section 3.1 win. That is the section covering installments and
the more specific of the two, while the table in section 3 is a summary of the payment
methods. The R$ 100,00 in the table matches the floor of the last band, which suggests
the summary took the highest value.

It is a choice, not an obvious reading: anyone adopting the table in section 3 offers
fewer installments across almost the whole catalogue.

---

## Part C · Traceability matrix

Each line links a rule to the code that applies it and to the test that proves it is
applied. Only the rules that became code are in here. The rest of the manual is served
to the model as the text of the section, and Part A is what says where each one came
from.

### Price and payment

| Rule | Source | Where it is applied | Test |
|---|---|---|---|
| PIX gives 5% off the list price | section 3 | `pricing.price_for_product` | `test_pix_discount_applies_to_list_price` |
| The PIX discount does not apply on top of a promotional price | section 6.2 | `pricing.price_for_product` | `test_pix_discount_does_not_stack_on_promotional_price` |
| A promotion switched off is neither applied nor mentioned | section 7.3, B-03 | `pricing._active_promotion` | `test_inactive_promotions_are_ignored` |
| Promotions do not stack with each other | section 6.2 | `pricing._active_promotion` | `test_promotions_never_stack_with_each_other` |
| Minimum installment of R$ 50,00 up to 3x | section 3.1 | `pricing.max_installments` | `test_installment_floor_up_to_three_times`, `test_installment_floor_applies_through_the_product_lookup` |
| Minimum installment of R$ 80,00 from 4x to 6x, and R$ 100,00 from 7x to 12x | section 3.1 | `pricing.max_installments` | `test_max_installments_respects_the_minimum_for_the_band` |
| Installments are calculated on the price the customer pays | section 3.1, section 6.2 | `pricing.price_for_product` | `test_installments_are_calculated_on_the_discounted_price` |
| Combining payment methods only above R$ 2.000,00 | section 3.1 | `pricing.price_for_product` | `test_combined_payment_uses_the_price_actually_charged` |
| Above R$ 2.000,00 the combination is allowed | section 3.1 | `pricing.price_for_product` | `test_combined_payment_allowed_above_the_threshold` |

### Catalogue

| Rule | Source | Where it is applied | Test |
|---|---|---|---|
| An empty category is reported as lack of stock, not as outside the scope | B-05 | `catalog.list_categories` | `test_categories_report_how_many_products_they_have` |
| A discontinued product does not come up in a search | B-01 | `catalog.search_products` | `test_search_leaves_out_discontinued_products` |
| The count per category leaves out the discontinued, so it agrees with the search | B-01 | `catalog.list_categories` | `test_the_category_count_agrees_with_what_the_search_offers` |
| The customer asks for aço strings and the spreadsheet stores steel | the load | `catalog.STRING_MATERIALS` | `test_the_customer_asks_for_aco_and_the_catalogue_says_steel` |
| A discontinued product is offered if the customer asks for it by name | B-01 | `catalog.get_product_details` | `test_discontinued_product_is_found_when_asked_for_by_name` |
| A product out of stock appears in the search, flagged | B-03 | `catalog.search_products` | `test_search_keeps_out_of_stock_products_and_marks_them` |
| The price filter uses the lowest amount the customer can pay | B-09 | `catalog.search_products` | `test_search_price_filter_uses_the_price_the_customer_can_pay` |
| The search returns 10 per page and reports the total found | B-09 | `catalog.search_products` | `test_search_caps_the_page_and_reports_the_total` |
| Accents and case do not get in the way of a search by name | the load | `catalog.fold`, `db.build_database` | `test_accents_do_not_break_a_name_search` |
| The customer finds the product by typing part of the name | section 7.1 | `catalog.get_product_details` | `test_product_details_found_by_part_of_the_name` |

### Orders

| Rule | Source | Where it is applied | Test |
|---|---|---|---|
| An order is only returned with the phone and e-mail matching the record | section 9, B-10, D-06 | `orders.get_order_status` | `test_order_is_returned_when_phone_and_email_both_match`, `test_a_wrong_phone_gets_nothing`, `test_a_wrong_email_gets_nothing` |
| One customer's credentials do not open another's order | section 9, B-10 | `orders.get_order_status` | `test_another_customers_credentials_do_not_open_this_order` |
| A non-existent order and a failed check give the same answer | B-10 | `orders.get_order_status` | `test_an_order_that_does_not_exist_looks_the_same_as_a_failed_check` |
| The total reported is the stored one, never recalculated | B-04 | `orders.get_order_status` | `test_the_stored_total_is_reported_never_recalculated` |
| A cancelled order reports the recorded reason | section 7.3 | `orders.get_order_status` | `test_a_cancelled_order_carries_the_reason` |
| Withdrawal window: 7 calendar days from receipt | section 4.1, B-11 | `orders._deadlines` | `test_deadlines_are_calculated_in_code_not_by_the_model`, `test_the_last_day_of_the_window_still_counts` |
| Defect exchange window: 30 calendar days from the purchase | section 4.2, B-11 | `orders._deadlines` | `test_deadlines_are_calculated_in_code_not_by_the_model` |
| Legal warranty: 90 days from receipt | section 8.1, B-11 | `orders._deadlines` | `test_deadlines_are_calculated_in_code_not_by_the_model` |
| A closed window is reported with the date it closed | section 4.1, D-14 | `orders._deadlines` | `test_an_expired_window_is_reported_as_expired` |
| An order not yet delivered has no withdrawal and no warranty window | B-11 | `orders._deadlines` | `test_an_order_not_yet_delivered_has_no_deadlines_to_report` |
| The expected delivery only counts as receipt if the order was delivered | B-11 | `orders.get_order_status` | `test_a_shipped_order_has_not_been_received_yet` |
| A cancelled or undelivered order has no defect exchange window | section 4.2, B-12 | `orders._deadlines` | `test_a_cancelled_order_has_no_exchange_window`, `test_an_undelivered_order_has_no_exchange_window_either` |
| Punctuation in the phone number does not fail the customer | B-10 | `db.digits_only` | `test_the_customer_may_type_the_phone_any_way_they_like` |
| An uppercase e-mail does not fail the customer | B-10 | `db.normalize_email` | `test_the_email_is_not_case_sensitive` |

### Policies

| Rule | Source | Where it is applied | Test |
|---|---|---|---|
| The lookup returns the exact section asked for, never the neighboring one | D-02 | `policies.get_section` | `test_subsection_returns_only_itself` |
| Asking for a section brings its subsections too | D-02 | `policies.get_section` | `test_section_includes_its_subsections` |
| A section that does not exist fails instead of returning the nearest one | D-02 | `policies.get_section` | `test_unknown_section_is_reported_not_invented` |
| The manual's index goes into the prompt, the text does not | D-02 | `policies.list_sections`, `persona.build_system_prompt` | `test_index_lists_every_section_and_subsection` |
| The manual's internal sections are out of the agent's reach | manual cover, section 7, section 10 | `policies.INTERNAL_SECTIONS` | `test_the_internal_sections_are_out_of_reach` |
| Blocking the internal ones does not affect the other sections | section 7 | `policies._parse_manual` | `test_blocking_section_seven_does_not_break_the_rest` |

### Agent

These are not store rules, they are guarantees about the loop that talks to the model.
They are here because this document's rule holds for every test in the repository.

| Guarantee | Source | Where it is applied | Test |
|---|---|---|---|
| A price reaches the model as text, never as a floating point number | D-14 | `agent._plain` | `test_prices_reach_the_model_as_text_never_as_floats` |
| The generic order-not-found message reaches the model intact | B-10 | `agent._build_dispatch` | `test_a_failed_order_check_says_nothing_about_the_order_existing` |
| The tool result goes back to the model before it answers | D-01 | `agent.Agent.respond` | `test_a_tool_call_runs_and_its_result_goes_back_to_the_model` |
| A question that needs no lookup does not cause one | D-01 | `agent.Agent.respond` | `test_a_plain_answer_makes_no_lookups` |
| A tool that fails hands the error back to the model without dropping the conversation | D-01 | `agent.Agent._run_tool` | `test_a_failed_lookup_is_handed_back_instead_of_crashing` |
| An unknown tool name does not take the turn down | D-01 | `agent.Agent._run_tool` | `test_an_unknown_tool_name_does_not_take_the_turn_down` |
| The loop stops and offers the team instead of spinning forever | D-01 | `agent.Agent.respond` | `test_the_loop_stops_instead_of_spinning` |
