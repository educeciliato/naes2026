---
name: mensagens-commit
description: Use sempre que for escrever uma mensagem de commit neste projeto — padrão Conventional Commits em português do Brasil, com tipos e escopos fixos, resumo no imperativo de até 72 caracteres e nenhum segredo.
---

## Formato

```
<tipo>(<escopo>): <resumo no imperativo>

<corpo opcional: o PORQUÊ da mudança, quebrado em ~72 colunas>

<rodapé opcional: BREAKING CHANGE: ..., Refs #12, Co-Authored-By: ...>
```

### Regras do assunto (primeira linha)

1. Até **72 caracteres** no total, contando tipo e escopo.
2. Resumo no **imperativo**, em português: "adiciona", "corrige", "remove",
   "extrai" — como quem completa a frase "este commit…". Nunca no passado
   ("adicionado", "corrigi", "fiz") nem no gerúndio ("adicionando").
3. Começa com letra minúscula e **não termina com ponto**.
4. Diz **o que muda para quem usa ou mantém o sistema**, não o nome do arquivo.

### Tipos

| Tipo | Quando |
| --- | --- |
| `feat` | funcionalidade nova para o usuário (tela, filtro, campo) |
| `fix` | correção de bug ou de comportamento errado |
| `refactor` | muda a estrutura sem mudar o comportamento |
| `perf` | desempenho (queries, `select_related`, `annotate`, cache) |
| `docs` | só documentação (AGENTS.md, docs/, skills, docstrings) |
| `test` | só testes |
| `style` | visual/formatação sem mudar regra (CSS, indentação) |
| `build` | dependências e empacotamento (`requirements.txt`) |
| `chore` | manutenção que não entra em outro tipo (`.gitignore`, limpeza) |

### Escopos

`farmacia`, `website`, `ia`, `assistente`, `deploy`, `docs`, `agentes`.
Opcional quando a mudança é transversal (ex.: `chore: ...`).

## Regras de conteúdo

1. **Um assunto lógico por commit.** Se o resumo precisa de "e" ligando duas
   coisas sem relação, são dois commits (`git add -p` ajuda a separar).
2. Migration vai no mesmo commit do model que a gerou.
3. Testes da funcionalidade podem ir no mesmo commit dela (`feat`).
4. **Nunca** coloque segredos na mensagem nem no diff: chaves, senhas, URLs
   de banco (`postgresql://...`), conteúdo de `.env` ou `app.yaml`. Antes de
   commitar: `git diff --cached` e procure `KEY`, `SECRET`, `PASSWORD`, `postgres`.
5. Não commite `db.sqlite3`, `__pycache__/`, `.env`, `app.yaml`,
   `static_gcloud/` nem `staticfiles/`.
6. Mudança que quebra compatibilidade leva `BREAKING CHANGE: <o que quebrou
   e como migrar>` no rodapé.

## Exemplos deste projeto

Bons:

```
feat(farmacia): filtra medicamentos por validade e laboratório
fix(website): corrige link do CSS que apontava para pharma.css
perf(farmacia): conta membros dos grupos com annotate
feat(ia): registra auditoria de toda chamada ao Gemini
feat(assistente): envia perguntas por AJAX com token CSRF
docs(agentes): cria AGENTS.md e skills do projeto
build: fixa google-genai, markdown e nh3 no requirements.txt
chore(deploy): tira app.yaml e staticfiles do controle de versão
```

Com corpo e rodapé:

```
refactor(farmacia): restringe registros ao dono também para staff

O requisito pede que só quem cadastrou liste, veja, altere e exclua.
Antes o staff via tudo; agora o get_queryset filtra sempre e o acesso
alheio dá 404.

BREAKING CHANGE: staff não vê mais os registros de outros usuários.
```

Ruins (e por quê) — inclusive do histórico deste repositório:

| Mensagem | Problema |
| --- | --- |
| `fix: as coisa coisaram` | não diz o que foi corrigido |
| `feat: hospedei o coisa` | passado, vago; deploy é `chore(deploy)` |
| `feat:adicionei mais uma classe (farmacia)` | sem espaço após `:`, passado, sem escopo |
| `ainda tem coisa para corrigir` | sem tipo, não descreve mudança |
| `feat(farmacia): Adiciona filtros.` | maiúscula no início e ponto final |
| `update views.py` | sem tipo, fala do arquivo e não da mudança |
| `feat: adiciona filtros, corrige CSS e atualiza o README` | três assuntos: separe |

## Passo a passo

1. `git status` e `git diff` — entenda tudo o que vai entrar.
2. Separe por assunto (`git add <arquivos>` ou `git add -p`).
3. `git diff --cached` — confira que não há segredo nem arquivo proibido.
4. Escolha tipo e escopo pelas tabelas acima.
5. Escreva o resumo no imperativo e conte os caracteres (≤ 72).
6. Se o porquê não for óbvio, escreva o corpo.
7. Commite. **Não faça `push`** sem pedido explícito.
