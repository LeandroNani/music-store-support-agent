# Catálogo de regras de negócio

O manual da loja é um texto em pdf, escrito para a equipe ler. Os dados estão em seis
planilhas. Para o Tom funcionar, cada regra do manual precisou virar código, e em
vários pontos o manual briga com os dados.

Este documento é esse trabalho: o que o manual manda, o que os dados mostram, e o que
foi decidido quando os dois discordam. Nenhum teste deste repositório existe sem uma
linha aqui.

- [Parte A: regras diretas do manual](#parte-a--regras-diretas-do-manual)
- [Parte B: conflitos entre o manual e os dados](#parte-b--conflitos-entre-o-manual-e-os-dados)
- [Parte C: matriz de rastreabilidade](#parte-c--matriz-de-rastreabilidade)

---

## Parte A · Regras diretas do manual

Regras onde o manual é claro e os dados não contradizem. Entram no código sem decisão
adicional.

### Preço e pagamento

| Regra | Origem |
|---|---|
| PIX dá 5% de desconto sobre o preço de tabela | §3 |
| O desconto do PIX não se aplica sobre preço já promocional | §6.2 |
| Promoções não são cumulativas entre si | §6.2 |
| Preço promocional é sempre apresentado junto do preço original e do percentual | §6.2 |
| Crédito em até 3x: parcela mínima de R$ 50,00 | §3.1 |
| Crédito de 4x a 6x: parcela mínima de R$ 80,00 | §3.1 |
| Crédito de 7x a 12x: parcela mínima de R$ 100,00 | §3.1 |
| Combinar formas de pagamento: só acima de R$ 2.000,00 | §3.1 |
| Boleto compensa em até 3 dias úteis | §3 |

> **Consequência no código:** o número máximo de parcelas depende do preço. Um produto
> de R$ 359,00 aceita até 4x (R$ 89,75, acima do mínimo de R$ 80,00), mas não aceita 5x
> (R$ 71,80) nem qualquer parcelamento na faixa de 7x a 12x.
>
> Nenhuma conta é feita pelo agente (D-14, que explica por quê). A função devolve o
> parcelamento já resolvido e o Tom comunica. Vale para desconto, preço no PIX e
> contagem de prazo. O frete não entra: o material recebido não dá a tabela.

### Trocas, devoluções e garantia

| Regra | Origem |
|---|---|
| Arrependimento: 7 dias corridos após o recebimento, sem justificativa | §4.1 |
| Arrependimento exige embalagem original, sem uso, com acessórios e manuais | §4.1 |
| Reembolso na mesma forma de pagamento, em até 10 dias úteis | §4.1 |
| Frete de devolução por conta da loja em caso de arrependimento | §4.1 |
| Defeito de fabricação: troca em até 30 dias corridos após a compra | §4.2 |
| Após 30 dias, a garantia é acionada com o fabricante; a loja pode intermediar | §4.2 |
| Troca por preferência: 7 dias, sujeita à disponibilidade do produto desejado | §4.3 |
| Não trocam: itens personalizados, liquidação marcada como venda final, boquilhas | §4.4 |
| Garantia legal: 90 dias contra defeito, contados do recebimento | §8.1 |
| Garantia do fabricante: varia de 6 meses a 2 anos | §8.2 |
| Garantia não cobre desgaste natural, mau uso, reparo de terceiros, dano estético | §8.3 |

### Frete

| Regra | Origem |
|---|---|
| Campo Grande e região: frete grátis acima de R$ 500,00 | §5.1 |
| Campo Grande e região: abaixo de R$ 500,00, taxa fixa de R$ 35,00 | §5.1 |
| Campo Grande e região: entrega em 1 a 3 dias úteis, por motoboy próprio | §5.1 |
| Outras cidades: PAC 5 a 12 dias úteis, SEDEX 2 a 5, Jadlog 3 a 8 | §5.2 |
| Todos os envios incluem seguro | §5.2 |
| Instrumentos de grande porte podem exigir cotação individual de frete | §5.2 |
| Código de rastreio: BR + 9 caracteres + BR, enviado quando o pedido é despachado | §5.3 |

> **Consequência no código:** a regra de frete grátis só vale para Campo Grande. Os
> clientes da base estão em cinco cidades, e 26 deles estão fora de Campo Grande.

### Atendimento e escopo

| Regra | Origem |
|---|---|
| Tom de voz informal mas profissional, sem linguagem robotizada | §7.1 |
| Nunca informar preço, estoque ou prazo sem consultar o sistema | §7.1 |
| A loja vende apenas instrumentos, não vende acessórios | §1, §7.1 |
| Acessórios citados: cordas, palhetas, cabos, cases, pedais, amplificadores | §1 |
| Pedido de acessório é redirecionado com educação, sugerindo loja parceira | §7.1 |
| Produto fora de estoque: informar e sugerir alternativas semelhantes | §7.3 |
| Produto descontinuado: informar e oferecer equivalente ou sucessor | §7.3 |
| Promoção vencida: informar com transparência e apresentar o preço atual | §7.3 |
| Nunca prometer desconto que não está vigente | §7.3 |
| Reclamação: ouvir com empatia, registrar, encaminhar. Retorno em 24h úteis | §7.3 |
| Horário: seg a sex 9h às 18h, sábado 9h às 13h, domingo e feriado fechado | §2 |
| Fora do expediente, informar o horário de retorno | §7.1 |

### Dados pessoais

| Regra | Origem |
|---|---|
| Dados do cliente são usados só para pedido, rastreio, promoções e obrigação legal | §9 |
| Dados não são compartilhados com terceiros para marketing | §9 |

---

## Parte B · Conflitos entre o manual e os dados

Aqui o material recebido não dá resposta. Cada item é uma decisão tomada.

### B-01 · Produto descontinuado com estoque disponível

O produto 136 (Ibanez Bass 2X, R$ 441,00) está marcado como `discontinued` e tem
**13 unidades em estoque**. O manual manda informar que produto descontinuado saiu do
catálogo e oferecer um equivalente, mas não previu que ainda houvesse peça na prateleira.

**Decidido:** não aparece em busca, porque não faz mais parte do catálogo que a loja
oferece. Mas se o cliente perguntar por ele pelo nome, o Tom oferece e avisa que é peça
de linha encerrada. Atende o manual sem jogar fora estoque que existe e que a loja quer
vender.

---

### B-02 · Produto de lançamento futuro que já foi vendido

O produto 130 (Kala KA-ABP-CTG Barítono) está marcado como `coming_soon` com 2 unidades,
mas aparece em dois pedidos já realizados: o pedido 3, entregue em dezembro de 2025, e o
pedido 14, pendente.

**Decidido:** o Tom não vende e informa que ainda não está à venda. O status é o campo que o sistema
expõe, e o Tom não deve inferir que um cadastro está errado só porque o histórico
discorda dele.

A inconsistência é problema de cadastro da loja. Em passo futuro, o painel administrativo
lista as inconsistências para o gerente corrigir na origem.

---

### B-03 · Produto ativo com estoque zerado e promoções desligadas

O produto 96 (Giannini GF-3D, R$ 799,90) está `active` com estoque **zero**, tem duas
promoções cadastradas (18% e 40%), **ambas desligadas** (`is_active = 0`), e já foi
vendido no pedido 4. O manual fala em promoção vencida; a planilha só sabe dizer
ligada ou desligada, sem data, então é desligada que o código aplica.

**Decidido:** a busca devolve todos os produtos que atendem ao pedido do cliente, cada um
marcado como **Em estoque** ou **Fora de estoque**. O produto faz parte do catálogo e só
está sem peça no momento, então o cliente precisa saber que ele existe. O Tom sugere
alternativa para o que estiver esgotado, como manda a §7.3.

Nenhuma das duas promoções pode ser mencionada, por estarem desligadas.

---

### B-04 · Total do pedido não bate com a soma dos itens

Em 2 dos 20 pedidos, o total gravado difere da soma dos preços dos itens:

| Pedido | Total gravado | Soma dos itens | Diferença |
|---|---|---|---|
| 3 | R$ 3.450,00 | R$ 3.498,00 | R$ 48,00 |
| 20 | R$ 1.400,00 | R$ 1.488,00 | R$ 88,00 |

**Decidido:** o total gravado é a verdade e o Tom nunca recalcula. Esse é o valor que
passou pela forma de pagamento, e a diferença provavelmente é desconto dado na venda e
não registrado por item. Recalcular faria o Tom informar um valor que o cliente nunca
pagou.

A divergência é problema de cadastro da loja. Em passo futuro, o painel administrativo
exibe esses pedidos para o gerente decidir o que fazer na origem.

---

### B-05 · Categorias que existem e não têm produto

O catálogo tem 9 categorias. Três estão vazias: Instrumentos de Sopro (Madeiras),
Instrumentos de Sopro (Metais) e Cordas Orquestrais. Se um cliente perguntar por um
saxofone ou um violino, a categoria existe mas não há o que vender.

**Decidido:** o Tom responde que a loja trabalha com a categoria e no momento não tem
peças disponíveis. A §1 do manual lista sopros e cordas orquestrais entre o que a loja
vende, então é falta de estoque e não falta de escopo. O cliente fica sabendo que pode
voltar.

---

### B-06 · Qual fonte vence quando o manual e os dados discordam

A §1 afirma que o catálogo tem mais de 300 instrumentos. A planilha de produtos tem 65.

O número em si não é o problema: o manual pode estar desatualizado, e o cliente não vai
conferir. O problema é o Tom afirmar qualquer coisa sobre disponibilidade com base no
manual em vez dos dados. Se ele disser "temos mais de 300 instrumentos, incluindo
sopros" e na pergunta seguinte não conseguir citar um saxofone, ele se contradiz dentro
da mesma conversa.

**Decidido:** dado verificável (produto, preço, estoque, tamanho do catálogo) vem da
planilha. Regra (troca, frete, pagamento, garantia, tom de voz) vem do manual. O Tom não
cita número total de produtos, porque não existe fonte confiável para esse número. A §7.1
já aponta nessa direção, ao proibir informar estoque sem consultar o sistema.

A §1 do manual chega inteira ao modelo, com o "mais de 300" dentro, então a decisão
precisa estar no prompt: ele instrui a tirar número de produto da ferramenta e a não
repetir o do manual. É regra de comunicação, não de cálculo, e por isso cabe ali.

---

### B-07 · Dois telefones diferentes no mesmo manual

A §1.2 informa o telefone (67) 3341-4444. A §7 informa que o canal de WhatsApp é o
(67) 3321-4500. O e-mail também aparece em duas formas, uma delas com acento no domínio.

**Decidido:** os dois telefones ficam, e o Tom informa o que fizer sentido na pergunta.
A §1.2 rotula o 3341-4444 como "Telefone / WhatsApp" e a §7 dá outro número para
WhatsApp, então é contradição mesmo, não é um fixo e um de texto. Para pergunta sobre
atendimento por mensagem vale o número da §7, que é a seção que trata disso.

Do e-mail, só a forma sem acento é endereço válido. A forma acentuada está na tabela
da §1.2, que o Tom pode ler, então a correção está no prompt junto com a do número de
produtos.

---

### B-08 · Como o preço é apresentado

O cliente pergunta quanto custa o Takamine GD20. A resposta é R$ 2.199,00, ou
R$ 2.199,00 e R$ 2.089,05 no PIX? A §6.2 exige que preço promocional apareça com o preço
original e o percentual, mas não diz se o desconto do PIX deve ser citado sem o cliente
perguntar.

**Decidido:** o Tom sempre mostra os dois, preço de tabela e preço no PIX. O manual quer
transparência total de preço, e informar a condição mais vantajosa é atendimento melhor.

Quando houver promoção ativa, a resposta mostra preço original, percentual e preço final,
e deixa explícito que o desconto do PIX **não** soma com o preço promocional.

> Essa regra é difícil de pegar numa revisão, porque os dois descontos somados dão um
> número que parece certo. Por isso o teste que prova que o PIX não incide sobre preço
> promocional é escrito antes do código de preço existir, e precisa ser visto falhando
> primeiro.

---

### B-09 · O que entra numa busca por faixa de preço

O enunciado sugere o caso *"quais opções de violões disponíveis custando até R$ 1.000?"*.
O filtro de preço usa o preço de tabela ou o preço com promoção? E o que acontece com
produto descontinuado e produto esgotado?

**Decidido:** o filtro usa o menor preço que o cliente consegue pagar, ou seja, o preço
já com promoção ativa e também o preço no PIX. O Giannini GNF-3 custa R$ 1.049,00 e sai
por R$ 996,55 no PIX, então entra na busca por "até R$ 1.000" com o aviso de que só
cabe no teto pagando no PIX. Esconder seria pior atendimento, porque o produto serve e só depende
da forma de pagamento.

Produto sem estoque aparece na lista, marcado como **Fora de estoque**. Produto
descontinuado fica de fora da busca, e só é oferecido se o cliente perguntar por ele
pelo nome.

---

### B-10 · Que dado o Tom pede para liberar informação de pedido

A decisão de arquitetura foi colocar a verificação de identidade como parâmetro
obrigatório da função, em vez de instrução no prompt. Falta definir qual dado. Cada
cliente tem nome, telefone, e-mail e cidade. Não há CPF nem senha.

**Como seria em produção.** No WhatsApp, o telefone de quem está falando já vem do
próprio canal, verificado, sem o cliente precisar informar. O número não seria
perguntado, seria lido da conexão, e o Tom pediria só o e-mail como segundo fator. Se a
pessoa informasse um telefone diferente do que está conectado, não haveria autorização.

**Decidido:** como este protótipo não tem integração com o WhatsApp, nenhum dado chega
verificado. Então o Tom pede **telefone e e-mail**, e os dois precisam bater com o
cadastro daquele pedido. Pedir os dois compensa, em parte, a ausência do fator que o
canal daria.

**Limitação:** telefone informado pelo cliente não é telefone verificado. Numa implantação
real, o número viria da sessão do WhatsApp e essa checagem passaria a valer de verdade.

### B-11 · De que data os prazos são contados

O manual conta o arrependimento e a garantia legal "a partir do recebimento do
produto". A planilha de pedidos não tem data de recebimento: tem `order_date`, que é
a data da compra, e `estimated_delivery`, que é a previsão de entrega.

**Decidido:** usar a `estimated_delivery` como data de recebimento, e apenas para pedidos
com situação `delivered`. É o campo mais próximo do que o manual pede, e para um pedido
já entregue a previsão passou. A troca por defeito, que o manual conta a partir da
compra e não do recebimento, usa a `order_date`.

Pedido que ainda não foi entregue não tem prazo de arrependimento nem de garantia
contado, porque nada foi recebido.

**Limitação:** previsão de entrega não é entrega. Um pedido que atrasou tem a data
errada, e para menos, o que encurta o prazo do cliente. Numa implantação real o campo
de recebimento viria da transportadora.

---

### B-12 · Troca por defeito num pedido que o cliente não recebeu

A §4.2 dá 30 dias corridos **após a compra** para trocar produto com defeito de
fabricação. O prazo conta da compra, não do recebimento, e é o único dos três assim.

Seguindo o texto ao pé da letra, o pedido 20, que foi cancelado por endereço inválido,
teria até 07/04/2026 para trocar por defeito. O mesmo vale para pedido pendente e para
pedido que ainda está a caminho.

**Decidido:** a janela só é informada para pedido entregue. A regra existe para trocar
um produto com defeito, e um pedido cancelado nunca pôs produto nenhum na mão do
cliente. A data de início continua sendo a da compra, como o manual manda.

Dizer a um cliente que teve o pedido cancelado que ele ainda pode trocar o produto até
uma data é pior do que não dizer nada: ele vai cobrar isso da loja.

---

### B-13 · O manual dá dois valores de parcela mínima

A tabela da §3 diz "Cartão de Crédito | Até 12x sem juros | Parcela mínima de
R$ 100,00". A §3.1 dá faixas: R$ 50,00 até 3x, R$ 80,00 de 4x a 6x, R$ 100,00 de 7x a
12x. Com a primeira leitura, o Yamaha C40 de R$ 599,90 sai em no máximo 5x. Com a
segunda, em 6x de R$ 99,98.

**Decidido:** valem as faixas da §3.1. É a seção que trata de parcelamento e a mais
específica das duas, enquanto a tabela da §3 é um resumo das formas de pagamento. O
R$ 100,00 da tabela bate com o piso da última faixa, o que sugere que o resumo pegou o
valor mais alto.

É escolha, não leitura óbvia: quem adotar a tabela da §3 oferece menos parcelas em
quase todo o catálogo.

---

## Parte C · Matriz de rastreabilidade

Cada linha liga uma regra ao código que a aplica e ao teste que prova que ela é
aplicada. Só entram aqui as regras que viraram código. O resto do manual é servido
ao modelo como texto da seção, e a Parte A é que diz de onde cada uma saiu.

### Preço e pagamento

| Regra | Origem | Onde é aplicada | Teste |
|---|---|---|---|
| PIX dá 5% sobre o preço de tabela | §3 | `pricing.price_for_product` | `test_pix_discount_applies_to_list_price` |
| O desconto do PIX não incide sobre preço já promocional | §6.2 | `pricing.price_for_product` | `test_pix_discount_does_not_stack_on_promotional_price` |
| Promoção desligada não é aplicada nem mencionada | §7.3, B-03 | `pricing._active_promotion` | `test_inactive_promotions_are_ignored` |
| Promoções não são cumulativas entre si | §6.2 | `pricing._active_promotion` | `test_promotions_never_stack_with_each_other` |
| Parcela mínima de R$ 50,00 até 3x | §3.1 | `pricing.max_installments` | `test_installment_floor_up_to_three_times`, `test_installment_floor_applies_through_the_product_lookup` |
| Parcela mínima de R$ 80,00 de 4x a 6x, e de R$ 100,00 de 7x a 12x | §3.1 | `pricing.max_installments` | `test_max_installments_respects_the_minimum_for_the_band` |
| Parcelamento é calculado sobre o preço que o cliente paga | §3.1, §6.2 | `pricing.price_for_product` | `test_installments_are_calculated_on_the_discounted_price` |
| Combinar formas de pagamento só acima de R$ 2.000,00 | §3.1 | `pricing.price_for_product` | `test_combined_payment_uses_the_price_actually_charged` |
| Acima de R$ 2.000,00 a combinação é liberada | §3.1 | `pricing.price_for_product` | `test_combined_payment_allowed_above_the_threshold` |

### Catálogo

| Regra | Origem | Onde é aplicada | Teste |
|---|---|---|---|
| Categoria sem produto é informada como falta de estoque, não como fora de escopo | B-05 | `catalog.list_categories` | `test_categories_report_how_many_products_they_have` |
| Produto descontinuado não aparece na busca | B-01 | `catalog.search_products` | `test_search_leaves_out_discontinued_products` |
| A contagem por categoria não conta o descontinuado, para bater com a busca | B-01 | `catalog.list_categories` | `test_the_category_count_agrees_with_what_the_search_offers` |
| O cliente pede corda de aço e a planilha grava steel | ETL | `catalog.STRING_MATERIALS` | `test_the_customer_asks_for_aco_and_the_catalogue_says_steel` |
| Produto descontinuado é oferecido se o cliente pedir pelo nome | B-01 | `catalog.get_product_details` | `test_discontinued_product_is_found_when_asked_for_by_name` |
| Produto esgotado aparece na busca, marcado | B-03 | `catalog.search_products` | `test_search_keeps_out_of_stock_products_and_marks_them` |
| O filtro de preço usa o menor valor que o cliente consegue pagar | B-09 | `catalog.search_products` | `test_search_price_filter_uses_the_price_the_customer_can_pay` |
| A busca devolve 10 por página e informa o total encontrado | B-09 | `catalog.search_products` | `test_search_caps_the_page_and_reports_the_total` |
| Acento e caixa não atrapalham a busca por nome | ETL | `catalog.fold`, `db.build_database` | `test_accents_do_not_break_a_name_search` |
| O cliente acha o produto digitando parte do nome | §7.1 | `catalog.get_product_details` | `test_product_details_found_by_part_of_the_name` |

### Pedidos

| Regra | Origem | Onde é aplicada | Teste |
|---|---|---|---|
| Pedido só é devolvido com telefone e e-mail batendo com o cadastro | §9, B-10, D-06 | `orders.get_order_status` | `test_order_is_returned_when_phone_and_email_both_match`, `test_a_wrong_phone_gets_nothing`, `test_a_wrong_email_gets_nothing` |
| Credencial de um cliente não abre o pedido de outro | §9, B-10 | `orders.get_order_status` | `test_another_customers_credentials_do_not_open_this_order` |
| Pedido inexistente e credencial errada dão a mesma resposta | B-10 | `orders.get_order_status` | `test_an_order_that_does_not_exist_looks_the_same_as_a_failed_check` |
| O total informado é o gravado, nunca recalculado | B-04 | `orders.get_order_status` | `test_the_stored_total_is_reported_never_recalculated` |
| Pedido cancelado informa o motivo registrado | §7.3 | `orders.get_order_status` | `test_a_cancelled_order_carries_the_reason` |
| Prazo de arrependimento: 7 dias corridos do recebimento | §4.1, B-11 | `orders._deadlines` | `test_deadlines_are_calculated_in_code_not_by_the_model`, `test_the_last_day_of_the_window_still_counts` |
| Prazo de troca por defeito: 30 dias corridos da compra | §4.2, B-11 | `orders._deadlines` | `test_deadlines_are_calculated_in_code_not_by_the_model` |
| Garantia legal: 90 dias do recebimento | §8.1, B-11 | `orders._deadlines` | `test_deadlines_are_calculated_in_code_not_by_the_model` |
| Prazo fechado é informado com a data em que fechou | §4.1, D-14 | `orders._deadlines` | `test_an_expired_window_is_reported_as_expired` |
| Pedido não entregue não tem prazo de arrependimento nem de garantia | B-11 | `orders._deadlines` | `test_an_order_not_yet_delivered_has_no_deadlines_to_report` |
| Previsão de entrega só vale como recebimento se o pedido foi entregue | B-11 | `orders.get_order_status` | `test_a_shipped_order_has_not_been_received_yet` |
| Pedido cancelado ou não entregue não tem janela de troca por defeito | §4.2, B-12 | `orders._deadlines` | `test_a_cancelled_order_has_no_exchange_window`, `test_an_undelivered_order_has_no_exchange_window_either` |
| A pontuação do telefone não reprova o cliente | B-10 | `db.digits_only` | `test_the_customer_may_type_the_phone_any_way_they_like` |
| Maiúscula no e-mail não reprova o cliente | B-10 | `db.normalize_email` | `test_the_email_is_not_case_sensitive` |

### Políticas

| Regra | Origem | Onde é aplicada | Teste |
|---|---|---|---|
| A consulta devolve a seção exata pedida, nunca a vizinha | D-02 | `policies.get_section` | `test_subsection_returns_only_itself` |
| Pedir uma seção traz também suas subseções | D-02 | `policies.get_section` | `test_section_includes_its_subsections` |
| Seção inexistente falha em vez de devolver a mais próxima | D-02 | `policies.get_section` | `test_unknown_section_is_reported_not_invented` |
| O índice do manual vai para o prompt, o texto não | D-02 | `policies.list_sections`, `persona.build_system_prompt` | `test_index_lists_every_section_and_subsection` |
| As seções internas do manual não são acessíveis ao agente | capa do manual, §7, §10 | `policies.INTERNAL_SECTIONS` | `test_the_internal_sections_are_out_of_reach` |
| Bloquear as internas não afeta as demais seções | §7 | `policies._parse_manual` | `test_blocking_section_seven_does_not_break_the_rest` |

### Agente

Estas não são regras da loja, são garantias do laço que conversa com o modelo. Estão
aqui porque a regra deste documento vale para todo teste do repositório.

| Garantia | Origem | Onde é aplicada | Teste |
|---|---|---|---|
| Preço chega ao modelo como texto, nunca como número de ponto flutuante | D-14 | `agent._plain` | `test_prices_reach_the_model_as_text_never_as_floats` |
| A mensagem genérica de pedido não encontrado chega ao modelo intacta | B-10 | `agent._build_dispatch` | `test_a_failed_order_check_says_nothing_about_the_order_existing` |
| O resultado da ferramenta volta para o modelo antes dele responder | D-01 | `agent.Agent.respond` | `test_a_tool_call_runs_and_its_result_goes_back_to_the_model` |
| Pergunta que não precisa de consulta não gera consulta | D-01 | `agent.Agent.respond` | `test_a_plain_answer_makes_no_lookups` |
| Ferramenta que falha devolve o erro ao modelo sem derrubar a conversa | D-01 | `agent.Agent._run_tool` | `test_a_failed_lookup_is_handed_back_instead_of_crashing` |
| Nome de ferramenta inexistente não derruba a conversa | D-01 | `agent.Agent._run_tool` | `test_an_unknown_tool_name_does_not_take_the_turn_down` |
| O laço para e oferece a equipe em vez de girar sem fim | D-01 | `agent.Agent.respond` | `test_the_loop_stops_instead_of_spinning` |
