# Suposições

O enunciado pede que ambiguidades sejam resolvidas com uma interpretação razoável e
documentadas. Este documento registra as ambiguidades do **enunciado**, e o que foi
assumido em cada uma.

As ambiguidades dos **dados**, que viram código e teste, estão em
[BUSINESS_RULES-PTBR.md](BUSINESS_RULES-PTBR.md).

---

## S-01 · O canal é WhatsApp, mas sem integração

**A ambiguidade.** O manual trata o WhatsApp como canal principal de atendimento remoto.
O enunciado não pede integração com nada.

**Assumido:** o WhatsApp é o canal da história, não um requisito técnico. O enunciado
aceita linha de comando, notebook, API ou interface simples, o que confirma que a
integração não é esperada. O que o WhatsApp define é o **tom**: mensagem curta, informal,
como quem responde no celular.

Isso tem uma consequência de segurança. No WhatsApp de verdade, o telefone de quem está
falando chega verificado pelo próprio canal, sem o cliente precisar digitar. Aqui não
existe esse dado, então quando o cliente pede informação de pedido o Tom precisa pedir
telefone e e-mail, e confiar no que foi digitado. É uma verificação mais fraca do que
seria em produção, e está registrada como limitação conhecida.

---

## S-02 · Idioma

**A ambiguidade.** O e-mail do processo exige que todas as respostas sejam em inglês. O
enunciado, o manual da loja e os dados estão em português, e a loja fica em Campo Grande.

**Assumido:** são dois públicos diferentes. A documentação do repositório, que é a
entrega avaliada, vai em inglês. O Tom responde no idioma em que o cliente falar com ele.

Durante o desenvolvimento, a documentação é escrita em português e traduzida ao final.

---

## S-03 · A data de referência

**A ambiguidade.** Os pedidos da base vão até março de 2026, e várias regras dependem de
data: 7 dias de arrependimento, 30 dias de troca por defeito, 90 dias de garantia legal.
O enunciado não diz em que momento o sistema está rodando.

**Assumido:** a data real do sistema. A variável de ambiente `EMPORIO_TODAY` permite
fixar uma data para reproduzir um exemplo ou rodar um teste.

O efeito é que os prazos de arrependimento dos pedidos da base já expiraram, e a resposta
correta do Tom passa a ser mais interessante: informar que o prazo venceu e dizer qual
regra ainda pode valer, como a garantia legal de 90 dias em caso de defeito.

---

## S-04 · O Tom só lê, nunca escreve

**A ambiguidade.** A §7.3 do manual manda registrar reclamações e encaminhar ao
responsável. Mas o material recebido é só leitura: não existe sistema de chamado, e as
planilhas não têm onde gravar nada.

**Assumido:** o Tom não tem nenhuma ferramenta de escrita. Ele não cria pedido, não
cancela, não altera cadastro e não registra reclamação em lugar nenhum. Ele consulta,
responde e auxilia. Diante de uma reclamação, acolhe, explica o procedimento e informa o
prazo de retorno de 24 horas úteis previsto no manual.

Além de ser o que os dados permitem, é a escolha mais segura. Um agente que conversa com
o público e tem permissão de alterar dados precisa de um nível de controle que está fora
do escopo de um protótipo.

---

## S-05 · Persistência do histórico de conversa

**A ambiguidade.** O enunciado deixa a critério, dizendo para implementar "se fizer
sentido para a experiência do usuário".

**Assumido:** histórico dentro da sessão, sim. Sem ele o Tom não entende
*"e o mais barato deles?"*, que é uma pergunta normal de quem está comparando produto.
Entre sessões, não: exigiria identificar o cliente de forma persistente, o que é
responsabilidade do canal real e não deste protótipo.

---

## S-06 · Dois canais de entrega

**A ambiguidade.** O enunciado manda responder o e-mail com o link do repositório. O
e-mail do processo manda enviar um PDF pelo Google Forms.

**Assumido:** as duas coisas. O PDF enviado pelo formulário contém o link do repositório
e um resumo das decisões, e o e-mail é respondido com o mesmo link.

---

## S-07 · O que é esperado de um protótipo

**A ambiguidade.** O enunciado pede um protótipo e diz que o foco é o agente funcionando
corretamente, sem definir o que fica de fora.

**Assumido:** fica de fora tudo que é operação e não é comportamento do agente.
Sem autenticação de usuário, sem deploy, sem container, sem integração contínua, sem
banco em servidor e sem monitoramento. O que entra é o agente correto, testado nas regras
que importam, e rodável na máquina de quem avalia.

---

## S-08 · Quem conversa com o Tom

**A ambiguidade.** O enunciado diz que o agente vai "auxiliar a equipe no atendimento".
Isso tem duas leituras: o Tom responde ao cliente, ou o Tom é uma ferramenta de consulta
que o atendente usa enquanto conversa com o cliente. As duas mudam tudo: a segunda não
precisa de verificação de identidade nenhuma, porque quem pergunta já é da loja.

**Assumido:** o Tom fala com o cliente. A §7 do manual já põe o assistente virtual no
canal de WhatsApp ao lado dos atendentes humanos, e o auxílio à equipe vem de absorver
as perguntas repetidas antes que elas cheguem a uma pessoa.

A consequência é a verificação de identidade. Se o Tom falasse com a equipe, pedir
telefone e e-mail para abrir um pedido seria atrito inútil.
