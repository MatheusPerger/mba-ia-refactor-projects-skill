# Entregavel

## A. Análise Manual 

### 1. Projeto code-smells-project

| Severidade | Descrição |
| --- | --- |
| Critico | O módulo models.py possui consultas expostas a SQL Injection (concatenação de strings em models.py:28, 47-50, 58-61, 68, 92, 109-111, 126-129, 140, 148-151, 155-166, 174, 188, 220, 279-281, 291-297). Como os parâmetros não são sanitizados, chamadas maliciosas podem executar comandos arbitrários, resultando em perda, extração de dados ou comprometimento total do banco. O /login (models.py:109-111) permite bypass de autenticação |
| Critico | Senhas/chaves escritas diretamente no código-fonte: SECRET_KEY em app.py:7, senhas de seed em database.py:75-79 |
| Critico | Retorna credenciais na rota /health: `secret_key` e `db_path` expostos em controllers.py:285-289 |
| Critico | Retorna e-mail e senha dos usuários na rota /usuarios (controllers.py:128-134, campo `senha` montado em models.py:72-87; também em /usuarios/<id>, models.py:89-103). Senhas armazenadas em texto puro, sem hash (models.py:126-129, database.py:75-79) |
| Critico | Endpoint /admin/query executa SQL arbitrário enviado no body, sem autenticação (app.py:59-78) |
| Alta    | São apagados dados das tabelas sem nenhuma restrição: POST /admin/reset-db, sem autenticação (app.py:47-57) |
| Alta    | "God Module", models.py concentra 4 domínios (produtos, usuários, pedidos, relatório) com SQL, mapeamento e regras de negócio (models.py:1-314); rotas e endpoints admin também misturados no app.py |
| Alta    | Conexão global mutável compartilhada com `check_same_thread=False` e criação de schema/seed dentro de `get_db()` (database.py:4-10, 14-84) |
| Médio   | N+1: listar pedidos roda uma query por item e outra por produto dentro do loop (models.py:171-201 e 203-233, duplicado). Também em criar_pedido, que consulta cada produto duas vezes (models.py:139-146 e 154-166) |
| Médio   | Regras de negócio de criação e atualização de produto espalhada: validações duplicadas em controllers.py:24-62 e 64-96 (a atualização não valida nome nem categoria), regra de desconto no relatório (models.py:256-262), notificações simuladas no controller (controllers.py:208-210, 247-250) |
| Médio   | As rotas chamam os models diretamente, acoplamento forte (app.py:11-30 registra controllers que chamam models.* com SQL); `health_check` acessa o banco direto no controller (controllers.py:264-274) |
| Médio   | Criação de pedido sem transação adequada nem controle de concorrência no estoque; cancelar pedido não devolve estoque (models.py:133-169, controllers.py:249-250) |
| Médio   | `except Exception` devolve `str(e)` ao cliente em todas as rotas (ex.: controllers.py:10-12, 21-22), vazando detalhes internos, sem error handler centralizado |
| Baixo   | Concatenação manual com str() (controllers.py:8, 57, 106, 208, 248; models.py em todas as queries) |
| Baixo   | Logging via print() (controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250; app.py:56, 83-86) |
| Baixo   | Magic numbers e listas soltas: faixas de desconto 10000/5000/1000 e 0.1/0.05/0.02 (models.py:257-262), categorias válidas (controllers.py:52), status de pedido (controllers.py:242) |
| Baixo   | `debug=True` fixo e host 0.0.0.0 (app.py:8, 88); campos `ambiente: "producao"` e `debug: True` fixos no health (controllers.py:286, 288); import `os` e `sqlite3` não usados (database.py:2, models.py:2) |
| Baixo   | Mapeamento de linha para dict repetido manualmente em 6 lugares (models.py:12-21, 31-40, 79-86, 95-102, 178-185/211-218, 304-313) |

### 2. Projeto ecommerce-api-legacy

| Severidade | Descrição |
| --- | --- |
| Critico | Credenciais hardcoded em utils.js:1-7 (dbUser, dbPass, paymentGatewayKey `pk_live_...`, smtpUser) versionadas no código-fonte |
| Critico | Número do cartão completo e chave do gateway de pagamento são escritos no log em AppManager.js:45 (`console.log`) |
| Critico | "God Class" AppManager.js: uma única classe cria o banco e schema, faz seed, define rotas, valida entrada, processa pagamento e executa SQL (linhas 4-139) |
| Alta    | Hash de senha falso em utils.js:17-23 (`badCrypto`): base64 repetido e truncado em 10 caracteres, sem salt, trivialmente reversível. Senha padrão "123456" quando não é informada (AppManager.js:68) |
| Alta    | Rota DELETE /api/users/:id (AppManager.js:131-137) deixa matrículas e pagamentos órfãos, não trata erro e responde sucesso mesmo com falha |
| Alta    | Regra de negócio (checkout, cálculo de receita, criação de usuário) dentro do handler da rota, sem camada de controller/service |
| Alta    | Estado global mutável em utils.js:9-10 (`globalCache`, `totalRevenue`); `totalRevenue` é exportado e nunca usado |
| Médio   | Callback hell no checkout (AppManager.js:37-77) e no relatório financeiro (80-129), sem async/await |
| Médio   | N+1 em /api/admin/financial-report (AppManager.js:83-126): queries por curso, por matrícula, por usuário e por pagamento. Erros em `err` dos callbacks internos são ignorados e `enrollments` pode ser undefined |
| Médio   | Checkout sem transação: matrícula, pagamento e audit log são inseridos separadamente; falha no meio deixa dados inconsistentes (AppManager.js:50-62) |
| Médio   | Validação de entrada fraca no checkout (AppManager.js:35): só checa presença, sem validar formato de e-mail ou cartão. Rotas admin sem nenhuma autenticação |
| Baixo   | Nomes de variáveis crípticos: `u`, `e`, `p`, `cid`, `cc`, `usr`, `eml`, `pwd`, `c_id` (AppManager.js:29-33) |
| Baixo   | Magic numbers/strings: `10000` iterações e `substring(0, 10)` (utils.js:19-22), `cc.startsWith("4")` para aprovar pagamento, status "PAID"/"DENIED" soltos |
| Baixo   | Banco em memória (`:memory:`) fixo em AppManager.js:7 e porta fixa em config; `console.log` no lugar de logger; mensagens de erro como texto puro e inconsistentes ("Erro DB", "Erro Matrícula") |
| Baixo   | Import `totalRevenue` não utilizado em AppManager.js:2 e nome "Frankenstein LMS" em app.js:13 |

### 3. Projeto task-manager-api

| Severidade | Descrição |
| --- | --- |
| Critico | Senhas com MD5 sem salt em models/user.py:27-32 (`hashlib.md5`), algoritmo quebrado e vulnerável a rainbow tables |
| Critico | O hash da senha é devolvido nas respostas: `User.to_dict()` inclui `password` (models/user.py:21), exposto em GET /users/<id>, POST /users, PUT /users/<id> e /login |
| Critico | Credenciais hardcoded: SECRET_KEY em app.py:13 e senha SMTP em services/notification_service.py:9-10 |
| Critico | `app.run(debug=True, host='0.0.0.0')` em app.py:34 expõe o debugger do Werkzeug (execução remota de código) em todas as interfaces |
| Alta    | Login retorna token falso `'fake-jwt-token-' + id` (routes/user_routes.py:210) e nenhuma rota tem autenticação/autorização: qualquer um pode criar admin (role no body), deletar usuários ou ver relatórios |
| Alta    | Regra de negócio e validação dentro das rotas (task_routes.py, user_routes.py, report_routes.py), apesar de existir pasta `services/`; ela só tem o `NotificationService`, que nem é usado nas rotas |
| Alta    | `report_routes.py` mistura relatórios com CRUD de categorias (linhas 157-223), responsabilidades sem relação em um mesmo blueprint |
| Médio   | N+1: GET /tasks faz `User.query.get` e `Category.query.get` dentro do loop (task_routes.py:41-57); GET /users usa `len(u.tasks)` por usuário (user_routes.py:22); /reports/summary faz query de tarefas por usuário (report_routes.py:55-56) e /categories faz count por categoria (163) |
| Médio   | Duplicação: cálculo de `overdue` repetido em 5 lugares (task_routes.py:30-39, 71-80, 283-287; user_routes.py:171-180; report_routes.py:34-43, 132-135) apesar de existir `Task.is_overdue()`; serialização manual de task duplicada em vez de `to_dict()`; listas de status/roles repetidas apesar das constantes em helpers.py:110-116 |
| Médio   | Validação duplicada e inconsistente: `process_task_data` em utils/helpers.py:57 não é usado, e as rotas revalidam por conta própria. `priority < 1` quebra com 500 se vier string; PUT /categories não valida `data` nulo (report_routes.py:196-197); `int(priority)` sem tratamento em /tasks/search (task_routes.py:261) |
| Médio   | `except:` genérico engole erros em várias rotas (task_routes.py:62, 236; user_routes.py:130, 149; report_routes.py:186, 207, 221) e mascara o problema real; sem error handler centralizado |
| Médio   | DELETE /users apaga as tarefas do usuário em cascata sem confirmação (user_routes.py:140-142); DELETE /categories não trata tarefas vinculadas |
| Baixo   | APIs deprecated: `datetime.utcnow()` (models, rotas, helpers) e `Model.query.get()` do SQLAlchemy 2.x (uso em todas as rotas); substitutos: `datetime.now(timezone.utc)` e `db.session.get()` |
| Baixo   | Imports não usados: `os, sys, json, datetime` em app.py:7, `json, os, sys, time` em task_routes.py:7, `hashlib, json` em user_routes.py:6, `json` em report_routes.py:8, vários em helpers.py:2-7 |
| Baixo   | Magic numbers e strings: prioridade 1-5, tamanho do título 3/200, senha mínima 4, `'#000000'`, 7 dias; as constantes existem em helpers.py:110-116 mas não são usadas |
| Baixo   | Logging via `print()` em rotas, helpers e serviço de e-mail; `type(x) == list` em vez de `isinstance`; if/else aninhados em `is_overdue` (models/task.py:50-60) |
| Baixo   | Configuração fixa em app.py:11-13 (URI do banco, secret) sem variáveis de ambiente |

## B. Construção da Skill

**Estrutura.** A skill `refactor-arch` fica em `.claude/skills/refactor-arch/` (cópia idêntica nos 3 projetos). O `SKILL.md` (156 linhas) é só o fluxo: Fase 1 (análise), Fase 2 (auditoria, com pausa obrigatória pedindo confirmação) e Fase 3 (refatoração + validação). O conhecimento de domínio fica em `references/`, carregado apenas quando a fase precisa:

| Área | Arquivo |
| --- | --- |
| Análise de projeto | `project-analysis.md` (heurísticas de linguagem, framework, banco e arquitetura) |
| Catálogo de anti-patterns | `anti-pattern-catalog.md` (20 itens, sinais de detecção e severidade) |
| Template de relatório | `report-template.md` |
| Guidelines de arquitetura | `architecture-guidelines.md` (camadas MVC e responsabilidades) |
| Playbook de refatoração | `refactoring-playbook.md` (20 transformações antes/depois) |
| Validação | `checklist.md` |

**Catálogo.** São 20 anti-patterns nas 4 severidades. CRITICAL: SQL Injection, credenciais hardcoded, exposição de dados sensíveis, senha insegura, endpoints admin/debug expostos, God Class. HIGH: regra de negócio no controller, estado global, ausência de auth, acoplamento forte. MEDIUM: N+1, duplicação, validação, erro genérico, falta de transação, callback hell. LOW: APIs deprecated, magic numbers, nomes ruins, logging por print. Os itens saíram da análise manual dos 3 projetos, então cada achado manual tem um padrão correspondente. APIs deprecated (ex.: `datetime.utcnow()`, `Model.query.get()`) têm entrada própria.

**Agnóstica de tecnologia.** Os sinais de detecção são descritos por comportamento ("query montada por concatenação", "query dentro de loop"), com exemplos em Python e JS, e não por nome de arquivo. A análise infere a stack por manifestos (`requirements.txt`, `package.json`) e imports. Na Fase 3 a skill adapta o MVC ao que já existe: monolito (projetos 1 e 2) é dividido do zero, e projeto parcialmente organizado (projeto 3) é reorganizado sem recriar o que já está certo.

**Desafios e soluções.**
- *Relatório sem linhas exatas:* o template passou a exigir `arquivo:linha` em cada finding e a ordenação CRITICAL → LOW.
- *Refatoração que quebrava o contrato:* a Fase 3 ganhou a etapa "mesmo contrato externo" (rotas, payloads e status preservados) e a validação com boot e chamada real aos endpoints.
- *Projeto 3 já em camadas:* a skill detectou problemas de segurança e qualidade mesmo com a estrutura parcial, e o playbook ganhou transformações que reaproveitam as pastas existentes.
- *Segurança vs. compatibilidade:* a remoção de rotas perigosas (`/admin/query`, `debug=True`) e a inclusão de auth mudam o comportamento original de propósito, e isso é informado no resumo da Fase 3.

## C. Resultados

### Resumo dos relatórios de auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
| --- | --- | --- | --- | --- | --- | --- |
| 1 — code-smells-project (Python/Flask) | 6 | 4 | 5 | 3 | 18 | [audit-project-1.md](reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy (Node/Express) | 4 | 4 | 5 | 3 | 16 | [audit-project-2.md](reports/audit-project-2.md) |
| 3 — task-manager-api (Python/Flask) | 4 | 3 | 4 | 4 | 15 | [audit-project-3.md](reports/audit-project-3.md) |

Todos cobrem os problemas da análise manual (≥ 5 findings e pelo menos 1 CRITICAL/HIGH em cada).

### Antes / depois

**Projeto 1 — code-smells-project** (4 arquivos planos → MVC em camadas)

| Antes | Depois |
| --- | --- |
| <pre>code-smells-project/<br>├── app.py<br>├── controllers.py<br>├── models.py<br>├── database.py<br>└── requirements.txt</pre> | <pre>code-smells-project/<br>├── app.py              (composition root)<br>├── config/<br>│   ├── settings.py<br>│   ├── database.py<br>│   ├── constants.py<br>│   └── logger.py<br>├── routes/             (produto, usuario, pedido, relatorio, sistema)<br>├── controllers/        (produto, usuario, pedido, relatorio, sistema)<br>├── services/           (regras de negócio, auth, errors)<br>├── repositories/       (SQL parametrizado)<br>├── models/             (produto, usuario, pedido)<br>├── views/              (serializers)<br>├── middlewares/<br>│   ├── auth.py<br>│   └── error_handler.py<br>├── .env.example<br>└── requirements.txt</pre> |

**Projeto 2 — ecommerce-api-legacy** (God Class `AppManager.js`)

| Antes | Depois |
| --- | --- |
| <pre>ecommerce-api-legacy/<br>├── src/<br>│   ├── app.js<br>│   ├── AppManager.js<br>│   └── utils.js<br>├── api.http<br>└── package.json</pre> | <pre>ecommerce-api-legacy/<br>├── src/<br>│   ├── app.js          (entry point)<br>│   ├── errors.js<br>│   ├── logger.js<br>│   ├── config/<br>│   │   ├── index.js<br>│   │   └── constants.js<br>│   ├── database/<br>│   │   ├── index.js<br>│   │   └── schema.js<br>│   ├── routes/index.js<br>│   ├── controllers/    (checkout, user, admin)<br>│   ├── services/       (checkout, user, report, password)<br>│   ├── models/         (course, enrollment, user)<br>│   └── middlewares/    (adminAuth, asyncHandler, errorHandler)<br>├── .env.example<br>├── api.http<br>└── package.json</pre> |

**Projeto 3 — task-manager-api** (já tinha models/routes/services/utils)

| Antes | Depois |
| --- | --- |
| <pre>task-manager-api/<br>├── app.py<br>├── database.py<br>├── seed.py<br>├── models/<br>│   ├── user.py<br>│   ├── task.py<br>│   └── category.py<br>├── routes/<br>│   ├── user_routes.py<br>│   ├── task_routes.py<br>│   └── report_routes.py<br>├── services/<br>│   └── notification_service.py<br>└── utils/<br>    └── helpers.py</pre> | <pre>task-manager-api/<br>├── app.py              (composition root)<br>├── seed.py<br>├── config/             (settings, constants, database)<br>├── routes/             (user, task, category, report, health)<br>├── controllers/        (user, task, category, report, health)<br>├── services/           (+ auth, validation, task, user...)<br>├── repositories/       (base, user, task, category)<br>├── models/             (user, task, category)<br>├── views/              (serializers)<br>├── middlewares/<br>│   ├── auth.py<br>│   ├── error_handler.py<br>│   └── logging_config.py<br>├── utils/              (clock, errors)<br>└── .env.example</pre> |

### Checklist de validação

Os três projetos passam em todos os itens:

- [x] **Fase 1:** linguagem, framework e domínio corretos; número de arquivos condiz (4, 3 e 15 arquivos de origem)
- [x] **Fase 2:** segue o template; findings com arquivo e linhas; ordenados CRITICAL → LOW; ≥ 5 findings; APIs deprecated incluídas (projeto 3: `utcnow`, `Query.get`); a skill pausa e pede confirmação antes da Fase 3
- [x] **Fase 3:** estrutura MVC; config extraída para `config/` com `.env.example` (sem hardcoded); models; views/routes; controllers; error handler centralizado; entry point claro; app inicia sem erros; endpoints originais respondem

### Logs das aplicações após a refatoração

Smoke test rodado após a refatoração (resumo dos logs):

```
# Projeto 1 (porta 5100)
GET /produtos -> 200 | GET /produtos/1 -> 200 | GET /health -> 200
GET /pedidos (sem token) -> 401 | POST /login (credencial inválida) -> 401

# Projeto 2 (porta 3100)
[INFO] Frankenstein LMS rodando na porta 3100...
POST /api/checkout -> {"msg":"Sucesso","enrollment_id":2}
GET /api/admin/financial-report (sem token) -> 401

# Projeto 3 (porta 5101, após seed.py)
GET /health -> 200 | GET /tasks -> 200 | GET /users -> 200 | GET /categories -> 200
GET /reports/summary (sem token) -> 401
```

### Observações por stack

- **Python/Flask (1 e 2 do tipo monolito):** a skill dividiu `models.py`/`controllers.py` em camadas, trocou SQL concatenado por queries parametrizadas e mandou segredos para variáveis de ambiente.
- **Node/Express:** o principal ganho foi desfazer a God Class, trocar callback hell por `async/await` e tirar o número do cartão do log. O catálogo (callback hell, estado global) funcionou sem ajuste específico para JS.
- **Projeto parcialmente organizado:** a skill achou problemas que a estrutura existente escondia (regra de negócio nas rotas, MD5, `debug=True`, N+1) e acrescentou `controllers/`, `repositories/` e `views/` em vez de recomeçar.
- **Mudanças intencionais de contrato:** rotas administrativas e relatórios passaram a exigir autenticação, e `/admin/query` foi removida. O resto do contrato foi mantido.

## D. Como Executar

**Pré-requisitos:** Claude Code instalado e autenticado (`claude`), Python 3.10+ (projetos 1 e 3) e Node.js 18+ (projeto 2).

**Executar a skill** (em cada projeto, a pasta `.claude/skills/refactor-arch/` já está presente):

```bash
cd code-smells-project   && claude "/refactor-arch"
cd ../ecommerce-api-legacy && claude "/refactor-arch"
cd ../task-manager-api   && claude "/refactor-arch"
```

A Fase 2 imprime o relatório e pergunta `Proceed with refactoring (Phase 3)? [y/n]`. Responda `y` para refatorar.

**Validar a refatoração:**

```bash
# Projeto 1 (porta 5000)
cd code-smells-project && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cp .env.example .env   # defina SECRET_KEY
export $(grep -v '^#' .env | xargs) && python app.py
curl localhost:5000/produtos ; curl localhost:5000/health

# Projeto 2 (porta 3000)
cd ecommerce-api-legacy && npm install && cp .env.example .env && npm start
# requisições de exemplo em api.http

# Projeto 3 (porta 5001)
cd task-manager-api && pip install -r requirements.txt
cp .env.example .env   # defina SECRET_KEY
python seed.py && python app.py
curl localhost:5001/health ; curl localhost:5001/tasks
```

A refatoração funcionou se o app sobe sem erros, os endpoints originais respondem (200) e as rotas protegidas retornam 401 sem token.
