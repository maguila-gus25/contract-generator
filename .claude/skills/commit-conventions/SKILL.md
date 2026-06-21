---
name: commit-conventions
description: "Convenções de commit e fluxo de branches para o Contract Generator. Use ao iniciar qualquer sprint/mudança no sistema, ao versionar trabalho com git, ou ao escrever mensagens de commit. Garante branches por sprint/mudança, commits atômicos (uma mudança lógica por commit) e mensagens no padrão Conventional Commits em português. Acione para: criar branch, fazer commit, agrupar mudanças, padronizar histórico git, iniciar nova feature/correção."
metadata:
  type: workflow
  language: pt-BR
  version: "1.0.0"
---

# Commit Conventions — Contract Generator

Fluxo de versionamento do projeto: **uma branch por sprint/mudança** + **commits
atômicos** + **mensagens padronizadas (Conventional Commits) em português**.

## Quando usar

- Ao iniciar qualquer sprint, feature, correção ou mudança no sistema.
- Sempre que for versionar trabalho com git neste repositório.
- Ao escrever ou agrupar mensagens de commit.

## Regras fundamentais

1. **Nunca commitar/pushar direto na `main`.** Toda mudança vive numa branch própria.
2. **Uma branch por sprint/mudança.** Crie a branch *antes* de começar a editar.
3. **Commits atômicos.** Cada commit contém **uma única mudança lógica** que deixa o
   repositório num estado coerente. Nada de commit "guarda-tudo".
4. **Mensagens em português**, no padrão Conventional Commits.
5. **Cadência automática:** conforme cada unidade lógica fica pronta, faça o commit
   na branch da sprint (sem esperar pedido explícito). O usuário revisa no final.

## Fluxo de trabalho (passo a passo)

### 1. Abrir a branch da sprint/mudança
Antes de qualquer edição, partindo de uma `main` atualizada:

```bash
git switch main
git pull --ff-only            # se houver remoto configurado
git switch -c <tipo>/<descricao-curta-kebab>
```

Padrão de nome: `<tipo>/<descrição-curta-em-kebab-case>`
- `feat/visualizador-pdf`
- `fix/porta-airplay-5000`
- `refactor/build-contrato`
- `chore/skill-commits`
- `docs/atualizar-readme`

Use o mesmo prefixo `<tipo>` que será predominante nos commits da branch.

### 2. Trabalhar em unidades atômicas
Implemente uma mudança lógica de cada vez. Quando uma unidade estiver completa e
coerente (compila / não quebra o app), faça o commit dela antes de seguir.

Stage **apenas** os arquivos daquela unidade — evite `git add -A` cego:

```bash
git add app/contracts.py
git commit -m "feat: adicionar rotas de visualização inline de PDF"
```

### 3. Encadear commits atômicos
Repita o ciclo editar → commitar para cada unidade. Exemplo de uma sprint de
"visualizador de PDF" dividida em commits atômicos:

```
feat: adicionar rotas de visualização inline de PDF
feat: criar template do visualizador com iframe
feat: adicionar botão "Visualizar" no dashboard
style: aplicar design system navy/gold (Trust & Authority)
```

### 4. Fechar a sprint
Ao terminar, apresente o resumo dos commits ao usuário. Só faça `push` / abra PR
**quando o usuário pedir** (ver "Push e Pull Request").

## Formato da mensagem (Conventional Commits)

```
<tipo>(<escopo opcional>): <assunto no imperativo, minúsculo, sem ponto final>

[corpo opcional: o quê e por quê — não o como]

[rodapé opcional: BREAKING CHANGE, refs de issue, co-autoria]
```

- **Assunto:** ≤ 72 caracteres, modo imperativo ("adicionar", não "adicionado").
- **Escopo** (opcional): área afetada — `feat(auth):`, `fix(viewer):`.
- **Corpo** (quando ajudar): explique a motivação, não a mecânica do diff.

### Tipos
| Tipo       | Quando usar                                                        |
|------------|--------------------------------------------------------------------|
| `feat`     | Nova funcionalidade para o usuário                                 |
| `fix`      | Correção de bug                                                    |
| `refactor` | Mudança de código sem alterar comportamento externo               |
| `style`    | Formatação, CSS, espaçamento — sem mudança de lógica              |
| `docs`     | Documentação (README, CLAUDE.md, comentários)                     |
| `test`     | Adição/ajuste de testes                                            |
| `chore`    | Build, deps, configs, tarefas de manutenção                       |
| `perf`     | Melhoria de performance                                            |

### Exemplos bons
```
feat: adicionar visualizador de PDF inline no dashboard
fix: usar porta 5001 para evitar conflito com AirPlay no macOS
refactor: extrair construção do Contrato para _build_contrato
docs: atualizar README com stack Flask + SQLite
chore: criar skill de convenções de commit
```

### Evite (anti-padrões)
```
update                          # vago, sem tipo
feat: várias coisas             # não atômico
Corrige bug e adiciona feature  # mistura dois tipos
WIP                             # não commitar trabalho incoerente na branch final
```

## Co-autoria

Os commits feitos pelo agente devem terminar com a linha de co-autoria:

```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

## Push e Pull Request

- `git push` e abertura de PR acontecem **apenas quando o usuário solicitar**.
- PR sempre da branch da sprint → `main` (nunca push direto na `main`).
- Rodar `pytest` antes de abrir PR (conforme `CLAUDE.md`).

## Checklist rápido

- [ ] Estou numa branch de sprint (não na `main`)?
- [ ] Cada commit é uma única mudança lógica coerente?
- [ ] O `git add` incluiu só os arquivos daquela unidade?
- [ ] A mensagem segue `<tipo>: <assunto imperativo>` em português?
- [ ] O app continua funcionando após o commit?
