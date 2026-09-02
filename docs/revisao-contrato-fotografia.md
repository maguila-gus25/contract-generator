# Revisão do contrato de fotografia — divergências para validar

> Versão em markdown da página enviada à Amanda:
> <https://claude.ai/code/artifact/2feb603e-c2a8-4445-b638-70c5c30479f8>
>
> Base de comparação: `Contrato longhiphotos.pdf`. Referente à reformulação
> descrita em [plano-reformulacao-fotografia.md](plano-reformulacao-fotografia.md).

Ao reescrever o gerador, o texto do contrato de produção fotográfica mudou em
14 pontos. Cada bloco abaixo tem o texto **como está hoje**, o texto **como
ficou** e o motivo. Os pontos das duas primeiras seções mexem no que o contrato
diz — são esses que dependem da validação da Amanda.

| | |
|---|---|
| Divergências | 14 pontos |
| Precisam de resposta | 4 pontos |
| Situação | Aguardando validação |

---

## 1. O que mudou de sentido

Aqui o contrato passou a dizer coisa diferente. São os pontos que precisam de
leitura antes de qualquer contrato novo sair.

### 1.1 O caput dizia que quem cancela é o contratado, mas cobrava a cliente

*Cancelamento · Quem cancela*

**Como está hoje**
> "Poderá o contrato ser cancelado pelo *contratado*" — e logo abaixo os itens
> a, b e c cobram multa *da cliente* conforme a antecedência do cancelamento.

**Como ficou**
> "Poderá o contrato ser cancelado pelo *CONTRATANTE*, observado o seguinte:" —
> seguido das mesmas três faixas de multa.

**Por quê** — As multas de 15%, 25% e 45% só fazem sentido cobradas de quem
desistiu do ensaio. Do jeito que estava, o parágrafo abria dizendo que quem
cancela é a fotógrafa e terminava cobrando multa da cliente.

### 1.2 O direito de cancelar indicando um substituto era da fotógrafa, não da cliente

*Cancelamento · Substituto*

**Como está hoje**
> "Poderá o *Contratante* cancelar o contrato mediante a devolução dos valores
> já pagos e a indicação de profissional substituto para a data do ensaio."

**Como ficou**
> "Parágrafo segundo: poderá o *CONTRATADO* cancelar o contrato mediante a
> devolução dos valores já pagos e a indicação de profissional substituto para
> a data do ensaio, não se responsabilizando pela contratação do substituto nem
> pelo valor por este cobrado."

**Por quê** — Devolver o valor pago e indicar outro fotógrafo é algo que só a
fotógrafa pode fazer. A cliente não tem o que devolver nem quem indicar.

### 1.3 A entrada virou metade exata do valor, calculada automaticamente

*Cláusula III · Preço*

**Como está hoje**
> "… o pagamento da importância de R$ 900,00, sendo R$ 450,00 a título de
> entrada, no dia da assinatura deste contrato, e o saldo de R$ 450,00 no dia do
> ensaio. Forma de pagamento: PIX." — os dois valores eram digitados à mão.

**Como ficou**
> "… o pagamento da importância de R$ 900,00, sendo R$ 450,00 no dia da
> assinatura deste contrato e R$ 450,00 no dia do ensaio, via PIX."

**Por quê** — O sistema divide o total em duas metades sozinho, então some um
campo do formulário e some a chance de os números não fecharem. Em valor com
centavo ímpar (R$ 901,01), a primeira parcela leva o centavo a mais: R$ 450,51 e
R$ 450,50. **Se a Amanda às vezes cobra entrada diferente de metade, isso volta
a ser um campo.**

### 1.4 Duas das três faixas de multa não diziam a palavra "multa"

*Cláusula VI · Faixas de cancelamento*

**Como está hoje**
> (a) … "com o pagamento de *multa de* 15% sobre o valor do contrato";
> (b) "com o pagamento de 25% sobre o valor do contrato";
> (c) "com o pagamento de 45% sobre o valor do contrato".

**Como ficou**
> As três faixas dizem a mesma coisa: "com o pagamento de *multa de* 15% / 25% /
> 45% sobre o valor do contrato".

**Por quê** — Sem a palavra, dá para ler os itens b e c como se fossem um
pagamento parcial do ensaio em vez de uma penalidade.

---

## 2. O que deixou de ser editável

Estas condições eram campos do formulário e agora estão escritas no texto. Se
alguma delas muda de cliente para cliente, precisa voltar a ser campo.

### 2.1 Onze campos viraram um: só a duração do ensaio continua editável

*Formulário · Condições do contrato*

| Condição | Valor fixado | Onde aparece |
|---|---|---|
| Multa de cancelamento até 28 dias | 15% | Cláusula VI |
| Multa de cancelamento até 21 dias | 25% | Cláusula VI |
| Multa de cancelamento até 7 dias | 45% | Cláusula VI |
| Multa por descumprimento | 25% | Cláusula IX |
| Plataforma de entrega | PIXIESET | Cláusula II |
| Prazo de entrega | 20 dias úteis | Cláusula IV |
| Retenção dos arquivos após a entrega | 20 dias | Cláusula IV |
| Comarca do foro | Florianópolis | Cláusula X |

**Por quê** — Preencher onze campos iguais a cada contrato só dava trabalho e
chance de erro. **Qualquer valor da tabela que não seja sempre o mesmo volta
para o formulário.** A ideia é que mais para a frente eles fiquem configurados
uma vez na conta, em vez de digitados por contrato — é a dívida registrada na
issue #16.

---

## 3. Defeitos corrigidos

Problemas do documento atual que o novo resolve. Não mudam o que o contrato diz.

### 3.1 Havia duas "Cláusula III" e a ordem pulava

*Numeração*

**Como está hoje**
> "CLÁUSULA III" aparece duas vezes — no Preço e no Prazo de Entrega. E a
> Cláusula Penal (XI) vem antes do Foro (IX).

**Como ficou**
> Dez cláusulas em romano, de I a X, na ordem em que aparecem. A numeração é
> calculada na hora de gerar, então não tem como repetir nem pular.

**Por quê** — Número de cláusula repetido é um problema real na hora de citar o
contrato numa discussão: "conforme a cláusula III" deixa de identificar uma
cláusula só.

### 3.2 O documento terminava na data, sem lugar para assinar

*Assinatura*

**Como está hoje**
> A última linha do contrato é a data. Não há linha de assinatura para nenhuma
> das partes.

**Como ficou**
> Cidade e data por extenso — "Florianópolis, 21 de agosto de 2026" — e abaixo
> duas colunas de assinatura, cada uma com linha, nome e CPF, marcadas
> CONTRATANTE e CONTRATADO.

**Por quê** — O contrato fala em "assinando-o em duas vias de igual teor" mas não
oferecia onde. A cidade vem do endereço cadastrado no perfil de contratado.

### 3.3 O rodapé mostrava "Página␣de", sem os números

*Rodapé*

**Como está hoje**
> "Página  de" — os campos de numeração do editor estavam quebrados e não
> imprimiam valor nenhum.

**Como ficou**
> "Página 1 de 3" em todas as páginas, gerado junto com o PDF.

**Por quê** — Num contrato impresso em duas vias, a paginação é o que garante
que não falta folha.

### 3.4 O número do contrato saiu do documento

*Cabeçalho*

**Como está hoje**
> "Contrato nº 001/2024" no topo, digitado à mão a cada contrato novo.

**Como ficou**
> O topo tem só o título e a data. O arquivo baixado é que carrega a
> identificação: `contrato-isabel-terra-2026-08-21.pdf`.

**Por quê** — Numerar contrato à mão é o tipo de coisa que só dá errado: número
repetido, sequência quebrada. O nome do arquivo com cliente e data acha o
contrato mais rápido do que qualquer número.

---

## 4. Apresentação

O texto é o mesmo; mudou como ele aparece na página. Nada aqui precisa de
aprovação, mas dá para ajustar.

### 4.1 As listas saíram de dentro do parágrafo

*Cláusulas I e VI*

**Como está hoje**
> "… estabelecem-se as seguintes definições: (a) Ensaio Fotográfico: sessão de
> fotos…; (b) Propriedade de imagem: detentor da imagem é…, e detentor dos
> direitos autorais é…; (c) Locação: local onde…" — tudo num parágrafo corrido.

**Como ficou**
> Cada definição é um item numerado (i, ii, iii) numa linha própria, e os dois
> lados da "propriedade de imagem" viram subitens (a, b) recuados abaixo dela.

**Por quê** — É a parte do contrato que a cliente mais precisa entender de
primeira. Em bloco corrido, ninguém lê até o (c).

### 4.2 As ressalvas ganharam nome e linha própria

*Cláusulas II, III, IV, VII, VIII e X*

**Como está hoje**
> "… contados a partir do dia do ensaio. O CONTRATADO reserva-se ao direito de
> deletar os arquivos…" — a ressalva vinha colada no fim do parágrafo principal.

**Como ficou**
> "Parágrafo único: o CONTRATADO reserva-se ao direito de deletar os arquivos…"
> — em parágrafo separado e recuado, como já era o caso na Cláusula II.

**Por quê** — Deixa cada cláusula com uma regra principal e as exceções
visivelmente penduradas nela. E dá o que citar: "parágrafo único da cláusula IV".

### 4.3 As partes são apresentadas em prosa, com endereço e contato

*Abertura*

**Como está hoje**
> Um bloco "PARTES" com CONTRATANTE e CONTRATADO em linhas separadas, com e-mail
> e endereço em formato de ficha.

**Como ficou**
> "**CONTRATANTE**: Isabel Terra Faillace Holanda, CPF nº 181.336.027-85, com
> domicílio na rua Servidão Piloto, Número 280, Campeche, Florianópolis, contato
> pelo telefone (48) 99656-5530 e e-mail isabelterra09@gmail.com."

**Por quê** — É o formato do contrato original. E ele se adapta: cliente
cadastrada só com nome e CPF sai "Fulana, CPF nº 000.000.000-00." — sem espaço
vazio nem vírgula sobrando.

### 4.4 Os acentos voltaram, e o texto ficou justificado

*Tipografia*

**Como está hoje**
> No PDF: "CONTRATO DE PRODUCAO FOTOGRAFICA", "clausulas e condicoes". A fonte
> usada não tinha os caracteres acentuados, então eles eram removidos.

**Como ficou**
> "CONTRATO DE PRODUÇÃO FOTOGRÁFICA". O documento passou a usar Barlow Condensed
> nos títulos e Source Serif no corpo, com o texto justificado.

**Por quê** — Contrato sem acento parece rascunho. As duas fontes são livres
(SIL OFL) e vão embutidas no PDF, então o documento abre igual em qualquer
computador.

### 4.5 O recuo passou a mostrar o que é regra e o que é exceção

*Hierarquia*

**Como está hoje**
> Todo parágrafo começa na mesma margem, com o mesmo espaço entre eles. A
> estrutura da cláusula só aparece se você ler.

**Como ficou**
> A regra principal encosta na margem; itens e ressalvas ficam recuados;
> subitens, mais um nível. E o espaço entre duas cláusulas é maior que entre
> dois parágrafos da mesma cláusula.

**Por quê** — É essa diferença de espaço que faz o olho ver onde uma cláusula
acaba e a outra começa, antes de ler uma palavra.

---

## O que depende da Amanda

1. Confirmar que **quem cancela é a cliente** e que o direito de indicar
   substituto é dela — pontos 1.1 e 1.2.
2. Dizer se a **entrada é sempre metade** do valor ou se às vezes muda — 1.3.
3. Passar a **tabela de condições fixadas** e apontar qualquer valor que não
   seja sempre o mesmo — 2.1.
4. Olhar o PDF novo e dizer se a **aparência** está boa — ainda dá para ajustar
   tamanho, espaço e fonte.

---

## Procedência dos pontos

Os pontos das seções 1 e 3 foram levantados na leitura do
`Contrato longhiphotos.pdf` durante a sessão de design; os das seções 2 e 4
descrevem o que mudou no gerador e são verificáveis no repositório. As
divergências 3.1 e 3.3 não foram reconferidas contra o PDF original, que não
está versionado aqui.
