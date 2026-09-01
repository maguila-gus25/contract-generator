# Plano — Reformulação do contrato de fotografia

> Origem: sessão de design (grilling) de 2026-09-01. Todas as decisões abaixo
> foram fechadas com o usuário; este documento é para execução, não para
> rediscussão. Dívida técnica assumida: issue #16.

## Resultado esperado

| | Hoje | Depois |
|---|---|---|
| Inputs (fotografia) | ~34 | 7 |
| Número do contrato | input obrigatório | não existe |
| Dados do contratado | 11 inputs por contrato | 0 (perfil da conta) |
| Dados do cliente | 11 inputs por contrato | 1 seletor (ou 11 na primeira vez) |
| Condições do contrato | 11 inputs | 1 (duração) |
| PDF | Helvetica sem acento, sem justificação, sem hierarquia | Barlow Condensed + Source Serif, justificado, cláusulas em romano com itens em 2 níveis |

**Os 7 inputs finais:** tipo · cliente · descrição · data do ensaio · valor ·
meio de pagamento · duração.

---

# PR 1 — `feat/perfil-e-agenda-de-clientes`

Objetivo: os dados das partes saem do formulário. Nada de documento ainda.

## 1.1 — Perfil de contratado no `User` (relação 1:1)

`app/models.py` — colunas novas em `User`, todas `nullable=True`:

```
contratado_nome, contratado_documento, contratado_tipo_documento,
contratado_email, contratado_telefone, contratado_cep, contratado_logradouro,
contratado_numero, contratado_complemento, contratado_bairro,
contratado_cidade, contratado_estado
```

Mais uma property:

```python
@property
def tem_perfil_contratado(self) -> bool:
    return bool(self.contratado_nome and self.contratado_documento)
```

**Sem campo `profissao`** — decidido na Q13.

## 1.2 — Modelo `Client`

`app/models.py`, tabela `clients`:

```
id, user_id (FK users.id), nome, documento, tipo_documento,
email, telefone, cep, logradouro, numero, complemento, bairro,
cidade, estado, created_at, updated_at
UniqueConstraint(user_id, documento)
```

- `User.clients` com `cascade="all, delete-orphan"` (conta excluída leva a agenda).
- **`documento` é obrigatório** — é a chave de deduplicação (Q15/Q31). Todo o
  resto é opcional (Q14: validação suave).
- Excluir um cliente **não** toca em `ContractRecord`: o nome já está copiado
  como texto em `contractor_name` (Q40).

## 1.3 — Migração das colunas

`app/__init__.py` já tem `_migrar_colunas_de_arquivo()`, que existe porque
`db.create_all()` não altera tabela existente. Generalizar para
`_migrar_colunas(tabela, colunas)` e chamar para `users` (12 colunas novas).
`clients` é tabela nova — `create_all()` resolve.

Testar o caminho de upgrade com um `contracts.db` pré-existente antes de subir,
e lembrar que em produção é Postgres (Neon), não SQLite.

## 1.4 — O número do contrato some

- `ContractRecord.number` **continua `NOT NULL`** — sem migração de esquema (Q34a).
  Passa a receber um valor derivado que nunca é exibido:
  `f"{slug(cliente)}-{data_inicio}"` → `isabel-terra-2026-08-21`.
- Adicionar `ContractRecord.nome_do_arquivo(fmt)` → `contrato-isabel-terra-2026-08-21.pdf`,
  usada por `download_contract` e `view_pdf` no lugar de `contrato_{number}.{fmt}`.
- `Contrato.validar()` (`contract_generator/models/contract.py`): remover a
  exigência de `numero` não vazio.
- Remover o input `number` de `new_contract.html`, a coluna do `dashboard.html`
  e a menção no flash de sucesso (`"Contrato gerado com sucesso!"`).
- Registros antigos mantêm o número gravado, mas ele deixa de aparecer.

## 1.5 — Formulário: contratado e contratante

`app/templates/new_contract.html`:

- **Seção Contratado**: renderiza **apenas** se `not current_user.tem_perfil_contratado`
  (Q12b). Quando renderiza, o POST grava o perfil. Quando não renderiza, um
  aviso discreto: "Contratado: Amanda Longhi · [editar em Minha conta]".
- **Seção Contratante**: no topo, `<select name="cliente_id">` com a agenda +
  opção "Novo cliente". Escolher um cliente preenche os 11 campos via JS; os
  campos continuam **editáveis** (correção vira upsert).

`app/static/js/clients.js` (novo): recebe a agenda serializada em JSON e
preenche os campos ao trocar o seletor. Convive com `cep.js`.

## 1.6 — Blueprint `clients_bp` (`app/clients.py`)

Página `/clientes` com CRUD (Q32b). Todas as rotas com `@login_required` e
checagem `client.user_id != current_user.id → abort(403)`.

```
GET  /clientes                  lista
GET/POST /clientes/<id>/editar  edição
POST /clientes/<id>/excluir     remove da agenda (histórico intacto)
```

Registrar no app factory. Link no nav do `base.html`. Todo form com
`csrf_token()`.

## 1.7 — Upsert ao gerar contrato

Em `new_contract` POST, depois de gerar com sucesso: procurar `Client` por
`(user_id, documento)`; existir → atualizar os campos; não existir → criar.
O cliente entra na agenda sozinho, sem checkbox (Q4).

## 1.8 — `/account`

Nova seção "Dados de contratado" reaproveitando os mesmos campos, para editar o
perfil depois do primeiro contrato.

## 1.9 — Testes

- `tests/test_clients.py`: isolamento entre usuários (403), upsert por documento,
  exclusão não apaga contrato, cliente sem documento é rejeitado.
- `tests/test_auth.py`: perfil de contratado gravado no primeiro contrato e
  reaproveitado no segundo.
- Ajustar os testes que hoje postam `number`.

---

# PR 2 — `feat/formulario-enxuto-fotografia`

Objetivo: chegar aos 7 inputs. Documento ainda sai igual.

## 2.1 — Metades do pagamento

`contract_generator/models/contract.py`, em `to_dict()`, dois derivados novos:

```python
"valor_metade_1": formatar_moeda(metade_1),
"valor_metade_2": formatar_moeda(metade_2),
```

Divisão exata em centavos (Q18a). Quando o total tiver centavo ímpar
(R$ 901,01), a primeira metade absorve o centavo — nunca some nem sobra dinheiro.
Cobrir isso com teste.

Como são chaves do núcleo, têm precedência sobre `extras` — nenhum template
consegue sobrescrever.

## 2.2 — `fotografia.json` enxuto

`campos` fica com **um** item: `duracao_horas` (padrão 2). Os outros 10 saem, e
seus valores entram cravados no texto das cláusulas (Q43/Q46c — **isto é a
dívida da issue #16**):

| Valor | Cláusula |
|---|---|
| 15% / 25% / 45% de cancelamento | VI |
| 25% de multa penal | IX |
| PIXIESET | II |
| 20 dias úteis de entrega | IV |
| 20 dias de retenção | IV |
| Florianópolis | X |

Chave nova no objeto do template: `"descricao_padrao": "Ensaio Fotográfico"`,
lida por `models/template.py` e usada para pré-preencher o campo.

Cláusula III passa a usar os derivados novos:

> Pelos serviços prestados, fica acordado o pagamento da importância de
> {valor}, sendo {valor_metade_1} no dia da assinatura deste contrato e
> {valor_metade_2} no dia do ensaio, via {forma_pagamento}. (…)

## 2.3 — Campos por tipo no formulário

`app/static/js/contract_fields.js` hoje só mostra/esconde a seção de condições.
Estender para governar também, por tipo:

| Campo | fotografia | servico / locacao |
|---|---|---|
| Data de fim | escondido e desabilitado | visível |
| Rótulo da data de início | "Data do ensaio" | "Data de Início" |
| Forma de pagamento | `<select>`: PIX (padrão), Dinheiro, Cartão de crédito, Cartão de débito, Transferência bancária | texto livre (como hoje) |
| Descrição | pré-preenchida "Ensaio Fotográfico", editável | vazia |

Campo escondido tem que ir **desabilitado**, para não entrar no POST — é o padrão
que o arquivo já usa.

## 2.4 — Testes

`tests/test_templates.py` valida que todo placeholder existe como campo
declarado ou chave de `to_dict()`. Com os campos removidos, o teste **vai
quebrar** — atualizar junto, e acrescentar `valor_metade_1`/`valor_metade_2` às
chaves conhecidas.

---

# PR 3 — `feat/redesign-do-documento`

Objetivo: o PDF ficar bonito. DOCX acompanha só a estrutura (Q24b).

## 3.1 — Cláusulas com itens em dois níveis

`contract_generator/models/clause.py` — `Clausula` aceita `itens`, opcional:

```json
{
  "numero": 1,
  "titulo": "DAS DEFINIÇÕES",
  "conteudo": "Para fins de entendimento do presente contrato, estabelecem-se as seguintes definições:",
  "itens": [
    {"texto": "Ensaio Fotográfico: sessão de fotos com direção artística (…)"},
    {"texto": "Propriedade de imagem:", "subitens": [
        "detentor da imagem é a pessoa captada na imagem;",
        "detentor dos direitos autorais é a pessoa que capta as imagens (fotógrafo)."
    ]},
    {"texto": "Locação: local onde é realizado o ensaio fotográfico (…)"}
  ]
}
```

Numeração: **romano minúsculo** no primeiro nível (i, ii, iii), **letras** no
segundo (a, b, c) — Q44a. Só dois níveis; não generalizar.

Reestruturar **todas as cláusulas com enumeração** (Q38c), não só a I e a VI.
Os desdobramentos em prosa ("Parágrafo primeiro:", "Parágrafo segundo:")
continuam sendo `conteudo`, não viram itens.

Documentar o formato novo no `CLAUDE.md`, seção "Templates de contrato".

## 3.2 — Fontes embutidas

`contract_generator/assets/fonts/` (Q27b, licença SIL OFL nos dois casos):

```
BarlowCondensed-Regular.ttf   BarlowCondensed-SemiBold.ttf
SourceSerif4-Regular.ttf      SourceSerif4-Bold.ttf   SourceSerif4-It.ttf
```

- Registrar com `pdf.add_font(...)` no `PdfGenerator`.
- **Conferir o `.vercelignore`** para os TTFs não serem excluídos do bundle
  (~500 KB).
- Com fonte Unicode, `rotulo_tipo(sem_acento=True)` perde a razão de existir:
  remover o parâmetro de `generators/base.py` e a chamada no gerador.
  "PRODUCAO" volta a ser "PRODUÇÃO".

## 3.3 — `pdf_generator.py` — reescrita

**Página**: A4, margens 25/20/25/20. Título centralizado **só na página 1**;
rodapé "Página X de Y" em todas via `footer()` + `alias_nb_pages()` (Q26a).

**Tipografia**:
- títulos de cláusula — Barlow Condensed SemiBold, caixa alta, entreletras ~0.08em
- corpo — Source Serif Regular, ~11pt, entrelinha ~1.45
- **justificado** (`align="J"`) em todo parágrafo de corpo

**Hierarquia** (Q37c):
- caput da cláusula encostado na margem esquerda
- parágrafos de desdobramento **recuados** (~8 mm) — em fpdf2, deslocando a
  margem esquerda temporariamente antes do `multi_cell`
- itens recuados, subitens mais um nível
- **espaçamento entre cláusulas maior que entre parágrafos da mesma cláusula** —
  é essa diferença que o olho lê como estrutura

**Qualificação das partes** — prosa, no formato do contrato original:

> **CONTRATANTE**: Isabel Terra Faillace Holanda, CPF nº 181.336.027-85, com
> domicílio na rua Servidão Piloto, Número 280, Campeche, Florianópolis, contato
> pelo telefone (48) 99656-5530 e e-mail isabelterra09@gmail.com.

A prosa **se adapta ao que existe** (Q14b): sem endereço, some o trecho do
domicílio; sem telefone, some o contato — sem vírgula órfã, sem "Número ,".
Testar com um cliente que só tem nome e CPF.

Depois das duas partes, o parágrafo de preâmbulo ("As partes acima identificadas
têm, entre si, justo e acertado o presente Contrato (…)").

**Numeração** — `CLÁUSULA I – DAS DEFINIÇÕES`, romano maiúsculo (Q25b). Gerado a
partir de `clausula.numero`, então a numeração duplicada do documento original
não se repete.

**Fecho** (Q28a):
1. "Florianópolis, 21 de agosto de 2026" — cidade do **perfil de contratado**,
   data por extenso
2. duas colunas de assinatura: linha, nome embaixo, **CPF** abaixo do nome

## 3.4 — `docx_generator.py`

Mesmas mudanças **estruturais**: sem número, qualificação em prosa, romanos,
itens em dois níveis, fecho com local/data e assinaturas. Refino tipográfico
não — o DOCX existe para ser editado à mão, não para impressionar (Q24b).

## 3.5 — Página de divergências para a Amanda (Q45b)

Ao reestruturar as dez cláusulas, anotar tudo que o JSON do repo diverge do
`Contrato longhiphotos.pdf` e publicar **uma página compartilhável** (artifact) —
não um arquivo no GitHub, que ela não vai abrir. Uma divergência por bloco:
texto original · texto novo · motivo.

Já mapeadas na sessão de design:

- **Cláusula V** — o caput diz "Poderá o contrato ser cancelado pelo
  **contratado**", mas os itens a/b/c cobram multa da **cliente**; e o parágrafo
  final atribui ao **Contratante** o direito de cancelar devolvendo valores e
  indicando profissional substituto, que é obviamente direito da **fotógrafa**.
  O JSON do repo já corrigiu os dois papéis.
- **Numeração** — "CLÁUSULA III" aparece duas vezes (Preço e Prazo de Entrega),
  e a XI (Cláusula Penal) vem antes da IX (Foro).
- **Rodapé** — "Página␣de", com os campos de numeração quebrados.
- **Ausência de bloco de assinatura** — o documento termina na data.

Acrescentar o que mais aparecer na revisão. É essa página que você manda pra ela
validar antes do merge.

## 3.6 — Testes

- PDF e DOCX gerando sem exceção para: cliente completo, cliente só com nome e
  CPF, valor com centavo ímpar, contrato com 10 cláusulas e itens aninhados.
- Numeração romana e a divisão em metades cobertas por teste unitário.
- Inspeção visual do PDF antes do merge — teste automatizado não vê feiura.

---

## Fora de escopo (não fazer nestes PRs)

- Configuração de condições por conta — issue #16, quando virar multiusuário
- Catálogo real de ensaios da Amanda (vira `<select>` quando ele chegar)
- Logo e identidade visual no documento (Q20c, depois)
- Enxugar serviço e locação (Q33a — herdam só o estrutural)
- Limpeza dos resíduos na raiz do repo (`contrato_001_2026.docx/pdf`, `output/`,
  `backend/`, `frontend/`) — vale um `chore/` separado

## Antes de cada PR

`pytest` verde, branch a partir de `main`, commits atômicos em Conventional
Commits/português (skill `commit-conventions`). Nunca commitar direto na `main`.
