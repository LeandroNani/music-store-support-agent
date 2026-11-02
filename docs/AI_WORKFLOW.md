# Uso de assistente de IA

> **RASCUNHO.** Leandro reescreve este arquivo com as próprias palavras antes da
> entrega. O texto abaixo é um ponto de partida, e o que estiver impreciso tem que ser
> corrigido por ele, porque este é o documento que fala dele.

> Documento em português durante o desenvolvimento. Tradução para inglês antes da entrega.

---

## Ferramenta

Claude Code, rodando no aplicativo de desktop da Anthropic.

## Como o trabalho foi conduzido

As decisões de arquitetura, produto e escopo são minhas. O assistente levanta as opções
e diz o que cada uma custa, eu escolho, e ele executa a escolha.

A ordem foi documentação antes de código. Antes de existir qualquer implementação, eu
defini a abordagem, registrei as decisões em [DECISIONS.md](DECISIONS.md) e montei o
catálogo de regras em [BUSINESS_RULES.md](BUSINESS_RULES.md). Esse catálogo é a
especificação contra a qual os testes foram escritos.

As restrições que impus ao assistente estão em [AGENTS.md](../AGENTS.md), dentro do
repositório. Elas cobrem arquitetura, escopo, testes, commits e estilo de escrita, e
valem para qualquer assistente que trabalhe neste projeto.

## O que foi delegado e o que não foi

**Delegado:** redação de rascunhos, implementação das ferramentas, montagem do banco em
memória a partir dos CSVs, escrita dos testes a partir do catálogo de regras, e a
interface.

**Não delegado:** a escolha da abordagem, o recorte do escopo, a decisão sobre cada
conflito entre o manual e os dados, a persona do Tom, e o texto final da documentação.

Os documentos deste repositório começaram como rascunho do assistente e foram
reescritos por mim.

## Commits

Commits que tiveram participação do assistente levam o rodapé `Co-Authored-By`. O
histórico mostra o progresso real do trabalho, sem reescrita.
