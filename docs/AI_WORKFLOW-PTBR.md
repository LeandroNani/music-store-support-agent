# Uso de assistente de IA

## Ferramenta

Claude Code, rodando no aplicativo de desktop da Anthropic.

## Como o trabalho foi conduzido

As decisões de arquitetura, produto e escopo são minhas. O assistente levanta as opções
e diz o que cada uma custa, eu escolho, e ele executa a escolha.

A ordem foi documentação antes de código. Antes de existir qualquer implementação, eu
defini a abordagem, registrei as decisões em [DECISIONS-PTBR.md](DECISIONS-PTBR.md) e montei o
catálogo de regras em [BUSINESS_RULES-PTBR.md](BUSINESS_RULES-PTBR.md). Esse catálogo é a
especificação contra a qual os testes foram escritos.

As restrições que impus ao assistente estão em [AGENTS-PTBR.md](../AGENTS-PTBR.md), dentro do
repositório. Elas cobrem arquitetura, escopo, testes, commits e estilo de escrita, e
valem para qualquer assistente que trabalhe neste projeto.

## O que foi delegado e o que não foi

**Delegado:** redação de rascunhos, implementação das ferramentas, montagem do banco em
memória a partir dos CSVs, escrita dos testes a partir do catálogo de regras, e a
interface.

**Não delegado:** a escolha da abordagem, o recorte do escopo, a decisão sobre cada
conflito entre o manual e os dados, a persona do Tom, e o texto final da documentação.

Os documentos deste repositório começaram como rascunho do assistente. Fui alterando,
acrescentando, corrigindo e editando o que era necessário, e conferindo o resto.

## Commits

Commits que tiveram participação do assistente levam o rodapé `Co-Authored-By`. O
histórico mostra o progresso real do trabalho, sem reescrita de histórico.
