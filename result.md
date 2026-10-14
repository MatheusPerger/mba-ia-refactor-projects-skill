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
