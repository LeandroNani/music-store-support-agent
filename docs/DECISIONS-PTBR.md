# Decisões técnicas

Cada decisão registra o problema, as alternativas que considerei, o que escolhi e,
quando existe, onde a escolha quebra.

## Índice

| # | Decisão | Em uma linha |
|---|---|---|
| [D-01](#d-01--laço-do-agente-escrito-à-mão) | Laço do agente escrito à mão | Laço próprio sobre o function calling nativo, sem framework de agente. |
| [D-02](#d-02--políticas-sem-banco-vetorial) | Políticas sem banco vetorial | Uma ferramenta devolve a seção pedida do manual, que tem 8 páginas e seções numeradas. |
| [D-03](#d-03--sem-agente-de-sql) | Sem agente de SQL | As perguntas de cliente são previsíveis, então as consultas são escritas à mão. |
| [D-04](#d-04--sqlite-em-memória) | SQLite em memória | Banco montado dos CSVs quando a aplicação sobe, sem alterar os arquivos originais. |
| [D-05](#d-05--regras-de-negócio-em-python) | Regras de negócio em Python | As regras ficam dentro das ferramentas, em código que pode ser testado. |
| [D-06](#d-06--verificação-de-identidade-dentro-da-função) | Verificação de identidade na função | A função exige dados de contato que batam com o cadastro antes de devolver o pedido. |
| [D-07](#d-07--streamlit-com-painel-de-trace) | Streamlit com painel de trace | Um painel lateral mostra quais ferramentas o agente consultou em cada resposta. |
| [D-08](#d-08--provedor-openai-gpt-6-luna) | Provedor OpenAI, GPT-6 Luna | Function calling nativo e maduro, que é o mecanismo central da arquitetura. |
| [D-09](#d-09--persona-tom-bilíngue) | Persona: Tom, bilíngue | Responde no idioma em que o cliente falar com ele. |
| [D-10](#d-10--nenhum-teste-sem-origem-rastreável) | Teste só com origem rastreável | Todo teste aponta para uma seção do manual ou uma anomalia nos dados. |
| [D-11](#d-11--data-real-como-referência) | Data real como referência | Os prazos são calculados sobre a data corrente, com variável de ambiente para fixar. |
| [D-12](#d-12--modelo-de-decisão-dedicado-fica-para-depois) | Modelo de decisão fica para depois | JEV encaixaria na classificação da mensagem, mas está em acesso antecipado. |
| [D-13](#d-13--teste-antes-do-código) | Teste antes do código | O teste é escrito antes da implementação e precisa ser visto falhando. |
| [D-14](#d-14--nenhum-cálculo-feito-pelo-modelo) | Nenhum cálculo feito pelo modelo | Toda conta é feita em Python e entregue pronta ao modelo. |
| [D-15](#d-15--escopo-de-segurança-do-protótipo) | Escopo de segurança do protótipo | A defesa está na arquitetura. Limites de uso ficam para a camada do canal. |
| [D-16](#d-16--estratégia-de-prompt) | Estratégia de prompt | Um prompt de sistema só, com o índice do manual injetado e nenhum exemplo. |
| [D-17](#d-17--tratamento-dos-dados) | Tratamento dos dados | O que a carga normaliza, e como o manual em pdf virou markdown. |

---

## D-01 · Laço do agente escrito à mão

**Problema.** O agente precisa decidir, a cada mensagem, se consulta o catálogo, o
manual de políticas, os dois ou nenhum.

**Considerei**
- LangChain, LlamaIndex ou equivalente
- Laço próprio sobre o function calling nativo do provedor
- Prompt único com todo o contexto embutido

**Escolhi o laço próprio.** O prompt único está fora porque elimina a decisão que o
enunciado pede para demonstrar. Os frameworks funcionam, mas escondem o laço atrás de
abstração pronta, e o que está em avaliação aqui é como eu estruturo a orquestração.
Também trazem dezenas de dependências para um problema de cinco ferramentas.

**Onde quebra.** Com dezenas de ferramentas, múltiplos agentes ou fluxos ramificados,
a abstração de um framework passa a pagar o próprio custo.

---

## D-02 · Políticas sem banco vetorial

**Problema.** O manual tem 8 páginas e 10 seções numeradas. O Tom precisa achar a
seção certa para cada pergunta.

**Considerei**
- Quebrar o texto em pedaços e buscar por similaridade de significado
- Colar o manual inteiro no prompt
- Converter para Markdown e expor uma ferramenta que devolve a seção pedida

**Escolhi a ferramenta por seção.** Busca por similaridade pode trazer meia seção ou a
seção vizinha, e o resultado varia. Buscar a seção numerada devolve o trecho exato,
sempre igual, sem infraestrutura nova. Colar o manual inteiro cabe no prompt, mas
apaga a decisão entre dados e políticas que o enunciado pede para demonstrar.

Isso continua sendo RAG, a técnica de buscar informação antes de responder. A parte
que ficou de fora é só a busca por similaridade.

**Onde quebra.** Acima de algumas dezenas de páginas, ou com texto sem seções claras,
a busca por similaridade passa a ser a escolha certa. Aí eu acrescentaria um conjunto
de testes de recuperação antes de confiar nela.

---

## D-03 · Sem agente de SQL

**Problema.** Uma alternativa é mostrar o esquema do banco ao modelo e deixar que ele
escreva as consultas.

**Considerei**
- O modelo escreve o SQL
- Consultas escritas à mão e parametrizadas, expostas como ferramentas

**Escolhi as consultas escritas à mão.** O critério é a previsibilidade, não o volume.
As cinco ferramentas cobrem o que o enunciado exemplifica: preço, disponibilidade,
faixa de preço, status de pedido e regra da loja.

O risco decisivo é outro. Se o modelo escreve a consulta, ele pode buscar na tabela de
promoções sem filtrar as inativas e prometer um desconto que não existe mais, o que a
seção 7.3 do manual proíbe. Com a consulta escrita à mão, esse erro é impossível.

**Onde quebra.** Perguntas analíticas fora do previsto não são atendidas. Um exemplo:
*"qual foi o ticket médio dos pedidos cancelados em fevereiro, separado por forma de
pagamento?"*. Se esse tipo de pergunta entrasse no escopo, o agente de SQL passaria a
valer, com conexão somente leitura, lista de tabelas permitidas e limite de tempo.

---

## D-04 · SQLite em memória

**Problema.** Os dados vêm em seis CSVs relacionados. Responder o status de um pedido
exige cruzar quatro deles: pedido, itens, produtos e cliente.

**Considerei**
- Ler os CSVs a cada consulta
- Carregar em pandas
- Carregar em SQLite na memória, quando a aplicação sobe

**Escolhi SQLite em memória.** O cruzamento de quatro tabelas vira uma consulta, em vez
de código manual repetido em cada ferramenta. `sqlite3` já vem com o Python, então não
adiciona dependência. E manter o banco só em memória deixa os CSVs originais intactos:
nada que o agente faz altera o material recebido.

**Onde quebra.** O banco é reconstruído a cada subida. Instantâneo neste volume,
inviável num volume grande.

---

## D-05 · Regras de negócio em Python

**Problema.** A loja tem regras como promoções não cumulativas, desconto PIX que não
incide sobre preço já promocional, e nunca confirmar disponibilidade sem checar estoque.

**Considerei**
- Escrever as regras no prompt e confiar que o modelo as siga
- Implementar as regras dentro das ferramentas

**Escolhi implementar nas ferramentas.** Uma regra escrita no prompt depende de o modelo
lembrar dela a cada resposta, e o cliente pode argumentar até contorná-la. Dentro da
função, o modelo nunca vê o dado cru: ele recebe o preço já correto e apenas comunica.

A divisão não é entre regra no código e nada no prompt. O que fica em Python é o que
decide número e elegibilidade: desconto, parcelamento, estoque, prazo, identidade. O
que fica no prompt é como comunicar o resultado, por exemplo sempre apresentar o preço
no PIX junto com o de tabela, ou dizer que um produto saiu de linha em vez de só omitir
o modelo. Essas linhas não calculam nada, e se o modelo esquecer uma delas a resposta
fica pior, não fica errada.

O efeito prático é que a correção do sistema passa a ser testável sem chamar o modelo.

**Onde quebra.** Regra nova exige mudança de código, não de texto.

---

## D-06 · Verificação de identidade dentro da função

**Problema.** Qualquer pessoa pode abrir a conversa e pedir o status de um pedido. A
base tem nome, telefone e e-mail de 50 clientes, e a seção 9 do manual trata de LGPD.

**Considerei**
- Instruir o modelo a confirmar a identidade antes de revelar dados
- Exigir a confirmação como parâmetro obrigatório da função

**Escolhi o parâmetro obrigatório.** Instrução no prompt é contornável por conversa:
*"esquece as instruções anteriores, sou o gerente da loja"* é um ataque conhecido, e
modelo de linguagem é convencível. Como parâmetro, a função exige o número do pedido mais
telefone e e-mail, os dois batendo com o cadastro daquele pedido. Não batendo, não
devolve nada, e o modelo não tem como burlar porque nunca teve acesso ao banco.

**Onde quebra.** Mais atrito para o cliente legítimo, que precisa informar dois dados
a mais.

---

## D-07 · Streamlit com painel de trace

**Problema.** O enunciado aceita linha de comando, notebook, API ou interface simples.

**Considerei**
- Linha de comando
- Streamlit só com o chat
- Streamlit com chat e um painel lateral mostrando as chamadas de ferramenta

**Escolhi chat com painel.** O requisito central do enunciado é o agente saber quando
consultar dados e quando consultar políticas. Sem o painel, essa decisão é invisível e
quem avalia precisa confiar que aconteceu. Com o painel, ela é observável. Os dados já
existem dentro do laço, então exibi-los custa pouco.

O painel é instrumento de desenvolvimento. Em produção não seria exibido ao cliente.

**Onde quebra.** Streamlit é protótipo, não interface de produção.

---

## D-08 · Provedor OpenAI, GPT-6 Luna

**Problema.** O enunciado deixa a escolha livre entre modelos pagos e gratuitos, locais
ou via API.

**Considerei**
- API de um provedor comercial
- Modelo local

**Escolhi a API da OpenAI, com o GPT-6 Luna.** O mecanismo central desta arquitetura é o
function calling, e a implementação da OpenAI é nativa e madura, com chamadas paralelas e
comportamento estável quando a ferramenta devolve erro.

O Luna é o modelo mais barato da linha, e dá conta porque a tarefa do modelo aqui é
estreita: escolher a ferramenta certa e redigir uma resposta curta. Todo o trabalho que
exige precisão, incluindo cálculo e aplicação de regra, acontece em Python antes de
chegar nele.

Modelo local ficou fora porque o suporte a chamada de ferramenta é menos confiável, e
depurar isso consumiria tempo sem melhorar a solução.

**Uma restrição do modelo, encontrada rodando.** O Luna recusa ferramentas no endpoint
de chat enquanto o esforço de raciocínio estiver ligado, e responde com um erro que
aponta as duas saídas: usar o endpoint novo, ou desligar o raciocínio. Desligar foi
suficiente, e não custa nada aqui: o raciocínio que este agente precisa é escolher a
ferramenta, e a deliberação que o parâmetro compra seria gasta num trabalho que o Python
já fez. O parâmetro é passado como opção, não fixo no código, porque outro modelo pode
não precisar dele.

**Onde quebra.** Rodar o projeto exige uma chave de API. O acesso ao provedor está
isolado em um módulo, então trocar de provedor ou de modelo é mudança localizada.

---

## D-09 · Persona: Tom, bilíngue

**Problema.** A seção 7.1 do manual descreve o tom de voz esperado, mas não dá nome ao
assistente. O material está em português e a entrega do processo seletivo é em inglês.

**Escolhi chamar o assistente de Tom, respondendo no idioma em que foi abordado.** O
enunciado pede uma persona alinhada à identidade da loja, e nome próprio é a forma mais
barata de tornar isso concreto. "Tom" referencia tom e semitom.

A resposta bilíngue resolve uma tensão real do material: em vez de escolher um idioma e
justificar a perda, o agente responde no idioma do cliente.

---

## D-10 · Nenhum teste sem origem rastreável

**Problema.** Teste automatizado só vale aqui se provar que as regras da loja são
cumpridas, e cobertura escolhida sem critério não demonstra isso.

**Escolhi exigir origem para todo teste.** Cada um aponta para uma seção específica do
manual ou para uma anomalia específica nos dados. O catálogo está em
[BUSINESS_RULES-PTBR.md](BUSINESS_RULES-PTBR.md).

Sem o catálogo, a suíte é um conjunto de verificações sem critério, e não há como
responder por que um caso foi testado e outro não.

---

## D-11 · Data real como referência

**Problema.** Os pedidos vão até março de 2026, e várias regras dependem de data: os 7
dias de arrependimento, os 90 dias de garantia legal.

**Considerei**
- Congelar uma data próxima ao último pedido
- Usar a data real

**Escolhi a data real.** Congelar a data esconderia justamente os casos em que a
regra de prazo importa. Com a data real, um pedido
entregue em fevereiro de 2026 já está fora do prazo de arrependimento, e a resposta
correta do Tom é informar que o prazo da seção 4.1 expirou e que a garantia legal de 90
dias ainda pode cobrir, se o caso for defeito de fabricação.

**Onde quebra.** Os exemplos de conversa envelhecem. Por isso existe a variável de
ambiente `EMPORIO_TODAY`, que fixa a data para reproduzir um exemplo ou rodar um teste.

---

## D-12 · Modelo de decisão dedicado fica para depois

**Problema.** Classificar a mensagem recebida, se é sobre catálogo, pedido, política ou
fora de escopo, hoje consome uma chamada completa de LLM.

**O que existe para isso.** JEV, da TypeSafe AI, é um modelo de decisão, não de
linguagem. Recebe uma entrada e um conjunto fechado de opções e devolve uma delas, com
grau de confiança. Como não gera texto, não consegue devolver nada fora do conjunto.

**Onde encaixaria.** Exatamente nessa classificação. Numa operação real, com volume alto
de mensagens por dia, mover essa etapa para um modelo de decisão reduz custo e latência,
e deixa o LLM só para o que ele faz melhor, que é redigir a resposta.

**Por que não agora.** O modelo está em acesso antecipado e eu não tenho acesso. Um
projeto que o avaliador não consegue executar é pior do que um projeto mais simples que
roda, e o enunciado exige instruções completas de execução.

Os ganhos de velocidade e custo divulgados variam bastante entre fontes e em boa parte
vêm de avaliações do próprio fabricante, então cito a capacidade, não os números.

---

## D-13 · Teste antes do código

**Problema.** As regras de negócio só valem se forem realmente garantidas. Teste escrito
depois do código tende a confirmar o que o código já faz, inclusive quando está errado.

**Escolhi escrever o teste primeiro, vê-lo falhar, e só então implementar.**

Um teste escrito depois do código pode passar sem estar medindo nada: olhando para o
campo errado, com uma condição que sempre dá verdadeiro, ou com um dado de entrada que
não exercita a regra. Nesses casos ele passa junto com os outros e ninguém percebe.
Vendo o teste falhar antes de existir a implementação, fica confirmado que ele mede o
que deveria medir.

A regra mais sensível do projeto é o desconto do PIX não incidir sobre preço já
promocional, porque os dois descontos somados produzem um número plausível e o erro
passa despercebido. Essa é a primeira que entra nesse ciclo.

**Onde quebra.** O ciclo confirma que cada teste mede o que deveria, mas não diz nada
sobre o que ficou sem teste. A prova mais forte seria teste de mutação, onde uma
ferramenta altera o código de propósito e verifica se algum teste reclama. Fica em
próximos passos.

---

## D-14 · Nenhum cálculo feito pelo modelo

**Problema.** Várias respostas do Tom envolvem conta: desconto, preço no PIX, número
máximo de parcelas, dias restantes de um prazo. O frete fica de fora: o material
recebido dá a regra de Campo Grande, não dá a tabela das outras cidades, então o Tom
lê a seção do manual e pede o CEP.

**Escolhi fazer toda conta em Python, dentro das ferramentas.** O modelo recebe o
resultado pronto e apenas comunica.

Um LLM prevê o próximo token, então aritmética para ele é padrão de texto, não cálculo.
Acerta quase sempre, e o erro sai com a mesma confiança do acerto. Informar valor de
parcela errado para um cliente é propaganda enganosa, que a §7.1 do manual manda
evitar.

Na prática, `get_product_details` devolve o parcelamento já resolvido, como 4x de
R$ 89,75. O Tom nunca divide 359 por 4.

**Onde quebra.** Toda conta nova exige mudança de código, em vez de um ajuste no
prompt.


---

## D-15 · Escopo de segurança do protótipo

**Problema.** Um agente que conversa com o público tem três riscos: vazar dado de um
cliente para outro, ser convencido a prometer condição que a loja não dá, e ser usado
para coisa que não tem nada a ver com a loja.

**O que já está resolvido pela arquitetura**

A verificação de identidade é parâmetro obrigatório da função, não instrução no prompt.
O modelo nunca recebe o pedido de um cliente sem que telefone e e-mail tenham batido com
o cadastro. Não existe no contexto dele um dado que ele possa ser convencido a revelar,
então o ataque do tipo "esqueça as instruções anteriores" não tem o que buscar.

Pela mesma razão, ele não consegue prometer um desconto que não vale mais: o preço chega pronto da
função. E não existe nenhuma ferramenta de escrita, então nada pode ser criado, alterado
ou apagado por conversa.

**O que foi considerado e deixado de fora**

Teto de tokens na resposta, teto no tamanho da mensagem recebida, teto de turnos por
conversa e contador de tentativas de verificação.

Os três primeiros cortam atendimento legítimo para impedir um caso hipotético: uma
resposta com dez produtos, cada um com preço, preço no PIX e parcelamento, passa de
qualquer teto razoável, e um cliente pode escrever uma mensagem longa descrevendo um
problema.

O contador de tentativas é diferente: ele não atrapalha ninguém, mas num protótipo sem
identidade persistente ele zera quando a pessoa abre outra conversa.

**Onde esses controles pertencem**

Limite de tentativas e limite de uso pertencem à camada do canal, por número de telefone,
onde o atacante não consegue zerar o contador sozinho. Alerta de gasto pertence à conta
da API. Nenhum dos dois é responsabilidade do agente.

**Um vetor que continua aberto**

Descrição de produto, observação de pedido e nome de cliente vêm das planilhas e entram
no contexto do modelo. Se alguém da loja cadastrar um produto cuja descrição contenha uma
instrução, ela chega ao modelo parecendo instrução legítima. Nos dados atuais isso não
acontece, mas o campo é texto livre preenchido pela loja.

O que reduz: as ferramentas devolvem dados estruturados com campos rotulados, em vez de
texto solto, e o prompt do sistema trata conteúdo vindo de ferramenta como dado. Não
elimina. Um detector de injeção foi descartado por ser contornável e por dar a impressão
de que o problema está resolvido.

**Onde quebra.** Tudo isto vale para um protótipo que roda na máquina de quem avalia.
Uma implantação real precisa dos limites no canal, de alerta de gasto, e de registro das
tentativas de verificação que falharam, para o gerente ver que alguém está varrendo
números de pedido.

---

## D-16 · Estratégia de prompt

**Problema.** O enunciado pede a justificativa da estratégia de prompt. As escolhas são
quantos prompts existem, o que entra em cada um, se há exemplos de conversa dentro dele
e se o modelo é instruído a raciocinar antes de responder.

**Considerei**
- Um prompt de sistema único, com as instruções de atendimento
- Dois estágios: um prompt classifica a mensagem, outro responde
- Incluir exemplos de pergunta e resposta dentro do prompt
- Pedir ao modelo que escreva o raciocínio antes de escolher a ferramenta

**Escolhi o prompt de sistema único, sem exemplos e sem raciocínio escrito.**

Um só porque a escolha entre dados e política já é feita pelo function calling: as cinco
ferramentas têm descrições que dizem para que servem, e o modelo escolhe entre elas. Um
estágio de classificação antes disso faria o mesmo trabalho duas vezes, e o segundo
estágio ainda precisaria montar os argumentos da chamada.

Sem exemplos porque o que um exemplo ensinaria é formato de resposta, e o formato aqui
vem pronto da ferramenta: o preço já chega com PIX e parcelamento resolvidos. Exemplo
de conversa também envelhece junto com o catálogo, e um exemplo com preço desatualizado
dentro do prompt é uma fonte de erro que ninguém vai testar.

Sem raciocínio escrito porque as decisões são de uma etapa: qual ferramenta chamar e com
que argumento. O `gpt-6-luna` roda com `reasoning_effort` desligado, o que torna a
escolha explícita em vez de acidental.

**O que fica dentro do prompt.** Como falar, o que fazer em cada situação que o manual
prevê, e o índice do manual: os números e títulos das seções, injetados a cada chamada
para o modelo saber qual pedir. O texto das seções não vai, o que mantém o prompt em
torno de cinco mil caracteres.

**O que não fica.** Nada que decida número ou elegibilidade (D-05). As linhas que
sobram são de comunicação, e se o modelo variar a forma delas a resposta muda de
redação, não de conteúdo.

**Onde quebra.** Prompt único cresce junto com o catálogo de situações. Quando o manual
passar de dez seções, o índice sozinho já ocupa espaço suficiente para valer uma busca
em vez da lista inteira. E sem exemplos, o tom depende só da descrição em prosa: se o
modelo mudar de versão, a redação pode mudar sem que nenhum teste perceba.

---

## D-17 · Tratamento dos dados

**Problema.** O enunciado pede a justificativa do tratamento dos dados. O material
recebido são seis CSVs e um manual em pdf, e nenhum dos dois está pronto para consulta.

**Escolhi normalizar na carga e nunca tocar nos arquivos originais.** Tudo que o ETL
faz está em `emporio/db.py`, roda quando a aplicação sobe, e os arquivos em `data/raw`
continuam byte a byte como vieram.

O que a carga resolve, e por que cada um apareceu:

- **Unicode NFC.** "Ponta Porã" aparece nos CSVs em duas formas Unicode diferentes, com
  o til como caractere separado em algumas linhas. Duas cidades iguais não batem numa
  comparação. Normalizar na carga é o único lugar onde isso se resolve uma vez.
- **Telefone reduzido a dígitos.** O cadastro guarda `(67) 99789-0123` e o cliente
  digita do jeito que quiser. A coluna derivada `phone_digits` existe para a comparação
  não depender de pontuação.
- **E-mail em minúscula.** Mesma razão, com `email_norm`.
- **Dobra de acento na busca.** `fold()` é registrada como função SQL e tira acento e
  caixa, senão "eletrico" não encontra "Elétrico". Fica no SQLite em vez de em Python
  para o filtro continuar dentro da consulta.
- **Corda de aço.** O catálogo grava `steel` e o cliente pede "aço". A tradução está em
  `catalog.STRING_MATERIALS`, não na carga, porque é vocabulário de quem pergunta e não
  defeito do dado.

**O manual em pdf.** O pdf não é lido em tempo de execução. Ele foi transcrito uma vez
para `data/store_policies.md`, preservando a numeração das seções, e é o markdown que a
ferramenta de políticas lê. O pdf continua versionado em `data/raw` para conferência.

A transcrição foi feita por um assistente e conferida por comparação, parágrafo a
parágrafo, contra o pdf: mesma numeração, mesmas tabelas, mesmo texto. A única diferença
é a capitalização do título da capa.

**Onde quebra.** A conferência da transcrição foi feita uma vez, à mão, e não há teste
que compare o markdown com o texto extraído do pdf. Se alguém editar o markdown, nada
acusa. Num projeto que fosse continuar, essa comparação viraria teste.

O ETL também confia no formato dos CSVs: uma linha com preço vazio derruba a subida da
aplicação com erro de conversão, em vez de ser reportada como linha inválida.
