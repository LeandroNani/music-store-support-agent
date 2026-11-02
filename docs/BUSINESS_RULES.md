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
| Crédito em até 3x: sem parcela mínima, exceto abaixo de R$ 50,00 | §3.1 |
| Crédito de 4x a 6x: parcela mínima de R$ 80,00 | §3.1 |
| Crédito de 7x a 12x: parcela mínima de R$ 100,00 | §3.1 |
| Combinar formas de pagamento: só acima de R$ 2.000,00 | §3.1 |
| Boleto compensa em até 3 dias úteis | §3 |

> **Consequência no código:** o número máximo de parcelas depende do preço. Um produto
> de R$ 359,00 aceita até 4x (R$ 89,75, acima do mínimo de R$ 80,00), mas não aceita 5x
> (R$ 71,80) nem qualquer parcelamento na faixa de 7x a 12x.
>
> LLM não é boa com cálculo: ela prevê o próximo token e o resultado não é
> determinístico. Então nenhuma conta é feita pelo agente. A função devolve o
> parcelamento já resolvido e o Tom comunica. Vale para desconto, preço no PIX, frete e
> contagem de prazo.

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
> clientes da base estão em cinco cidades, e 25 deles estão fora de Campo Grande.

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

**Decidido:** o Tom não vende e informa a previsão. O status é o campo que o sistema
expõe, e o Tom não deve inferir que um cadastro está errado só porque o histórico
discorda dele.

A inconsistência é problema de cadastro da loja. Em passo futuro, o painel administrativo
lista as inconsistências para o gerente corrigir na origem.

---

### B-03 · Produto ativo com estoque zerado e promoções vencidas

O produto 96 (Giannini GF-3D, R$ 799,90) está `active` com estoque **zero**, tem duas
promoções cadastradas (18% e 40%), **ambas vencidas**, e já foi vendido no pedido 4.

**Decidido:** a busca devolve todos os produtos que atendem ao pedido do cliente, cada um
marcado como **Em estoque** ou **Fora de estoque**. O produto faz parte do catálogo e só
está sem peça no momento, então o cliente precisa saber que ele existe. O Tom sugere
alternativa para o que estiver esgotado, como manda a §7.3.

Nenhuma das duas promoções pode ser mencionada, por estarem vencidas.

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
vende, então não é fora de escopo, é falta de estoque. É a resposta verdadeira, e deixa
a porta aberta para o cliente voltar.

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

---

### B-07 · Dois telefones diferentes no mesmo manual

A §1.2 informa o telefone (67) 3341-4444. A §7 informa que o canal de WhatsApp é o
(67) 3321-4500. O e-mail também aparece em duas formas, uma delas com acento no domínio.

**Decidido:** os dois telefones ficam. Ter um fixo para ligação e um para atendimento por
texto é o padrão de loja no Brasil, então não é contradição, e o Tom informa o que fizer
sentido na pergunta. Do e-mail, só a forma sem acento é endereço válido, e é a única que
o Tom usa.

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
já com promoção ativa e também o preço no PIX. Se um violão de R$ 1.050,00 sai por
R$ 997,50 no PIX, ele entra na busca por "até R$ 1.000", com o aviso de que só cabe no
teto pagando no PIX. Esconder seria pior atendimento, porque o produto serve e só depende
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

---

## Parte C · Matriz de rastreabilidade

Preenchida conforme a implementação avança. Cada linha liga uma regra ao código que a
aplica e ao teste que prova que ela é aplicada.

| Regra | Origem | Onde é aplicada | Teste |
|---|---|---|---|
| _a preencher_ | | | |
