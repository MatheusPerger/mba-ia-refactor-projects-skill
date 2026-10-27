================================
PHASE 2: ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   15 analyzed | ~1160 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] Credenciais hardcoded
**File:** `app.py:12`, `services/notification_service.py:9-10`

**Description:** `SECRET_KEY = 'super-secret-key-123'` e o usuário/senha SMTP (`taskmanager@gmail.com` / `senha123`) estão escritos no código-fonte e versionados.

**Impact:** Quem tem acesso ao repositório obtém a chave da aplicação e a conta de e-mail. Não dá para trocar o segredo sem alterar o código.

**Recommendation:** Ler os valores de variáveis de ambiente em `config/settings.py` e falhar no boot se faltarem (playbook #2).

### [CRITICAL] Armazenamento inseguro de senha
**File:** `models/user.py:29`, `models/user.py:32`

**Description:** `set_password` e `check_password` usam MD5 sem salt. O MD5 é rápido e quebrável por rainbow table.

**Impact:** Um vazamento do banco expõe as senhas dos usuários em segundos.

**Recommendation:** Usar `werkzeug.security.generate_password_hash` / `check_password_hash` (playbook #4). Fazer rehash das senhas legadas no próximo login.

### [CRITICAL] Exposição de dados sensíveis
**File:** `models/user.py:21`, `routes/user_routes.py:33`, `routes/user_routes.py:85`, `routes/user_routes.py:129`, `routes/user_routes.py:209`

**Description:** `User.to_dict()` inclui o campo `password` (hash MD5), devolvido em GET/POST/PUT de usuários e no login.

**Impact:** Qualquer cliente recebe o hash da senha de qualquer usuário, o que facilita o roubo de contas.

**Recommendation:** Serializador com lista explícita de campos públicos, sem `password` (playbook #3).

### [CRITICAL] Modo debug exposto
**File:** `app.py:34`

**Description:** `app.run(debug=True, host='0.0.0.0', port=5001)` fixos. O debugger do Werkzeug fica acessível em todas as interfaces de rede.

**Impact:** Permite execução remota de código por qualquer pessoa que alcance o servidor.

**Recommendation:** Ler `DEBUG`, `HOST` e `PORT` da config, com debug desligado e host `127.0.0.1` por padrão (playbook #5 e #20).

### [HIGH] Regra de negócio nas rotas
**File:** `routes/task_routes.py:11-63`, `routes/task_routes.py:273-299`, `routes/user_routes.py:153-183`, `routes/report_routes.py:12-155`

**Description:** Os handlers HTTP calculam atraso (overdue), estatísticas, taxas de conclusão e relatórios, e acessam `db`/`Model.query` diretamente. Não há camada de controller nem de service. `Task.is_overdue()` existe e é ignorada.

**Impact:** A regra não pode ser testada sem subir o servidor, e a lógica é copiada entre rotas.

**Recommendation:** Mover as regras para `services/` (task, user, report, category), deixar controllers só com o fluxo HTTP e as consultas nos models (playbook #6 e #7).

### [HIGH] Ausência de autenticação/autorização
**File:** `routes/user_routes.py:185-211`, `routes/user_routes.py:52`, `routes/user_routes.py:71-78`, `routes/user_routes.py:119-122`

**Description:** Nenhuma rota é protegida. O login devolve um token falso (`'fake-jwt-token-' + id`) e o `role` vem direto do body, então qualquer um cria um admin.

**Impact:** Qualquer cliente apaga usuários, vê relatórios e se promove a admin. O token falso dá falsa sensação de segurança.

**Recommendation:** Middleware de autenticação com token assinado e checagem de papel nas rotas sensíveis (playbook #9). Mudar o contrato exige decisão do usuário.

### [HIGH] Acoplamento forte e responsabilidades misturadas
**File:** `routes/report_routes.py:157-223`, `routes/task_routes.py:1-9`, `routes/user_routes.py:1-8`

**Description:** O blueprint `reports` também hospeda o CRUD de `/categories`. As rotas importam `db` e os models diretamente. `NotificationService` é instanciado por dentro e nunca é usado pelas rotas.

**Impact:** Mudar o banco ou o serviço exige mexer em vários arquivos, e não dá para usar mocks nos testes.

**Recommendation:** Separar rotas por domínio (categories em seu próprio blueprint) e montar as dependências no entry point (playbook #6 e #10).

### [MEDIUM] Query N+1
**File:** `routes/task_routes.py:41-57`, `routes/user_routes.py:22`, `routes/report_routes.py:55-68`, `routes/report_routes.py:163`

**Description:** Dentro de laços, o código faz `User.query.get`, `Category.query.get`, `len(u.tasks)` e `Task.query.filter_by(...)` por item.

**Impact:** O número de queries cresce com o volume, e listagens e relatórios ficam lentos.

**Recommendation:** Usar `joinedload` ou agregação com `GROUP BY`/`IN (...)` (playbook #11).

### [MEDIUM] Código duplicado
**File:** `routes/task_routes.py:30-39`, `routes/task_routes.py:71-80`, `routes/task_routes.py:283-287`, `routes/user_routes.py:171-180`, `routes/report_routes.py:34-36`, `routes/report_routes.py:132-135`

**Description:** A regra de overdue está copiada em 6 pontos. A serialização de task (`task_routes.py:17-28`, `user_routes.py:162-169`) e a validação de task/e-mail (`create_task`/`update_task` vs `process_task_data`/`validate_email`, que ficam sem uso em `utils/helpers.py`) também se repetem.

**Impact:** Uma correção feita em um lugar é esquecida nos outros, e criar e atualizar divergem.

**Recommendation:** Reutilizar `Task.is_overdue()` e `to_dict()`, e centralizar a validação em um único módulo (playbook #12).

### [MEDIUM] Validação de entrada ausente ou inconsistente
**File:** `routes/task_routes.py:113`, `routes/task_routes.py:182`, `routes/task_routes.py:261`, `routes/task_routes.py:264`, `routes/report_routes.py:196-202`, `routes/user_routes.py:125`

**Description:** `priority < 1` com valor não numérico, `int(priority)`/`int(user_id)` sem tratamento, `request.get_json()` possivelmente `None` no PUT de categoria e `active` sem checar o tipo. O update de task não aplica o `strip` nem a checagem de tipo do título.

**Impact:** Entradas inesperadas geram erro 500 ou gravam dados inválidos.

**Recommendation:** Validação centralizada que devolve 400 e é usada em criar e atualizar (playbook #13).

### [MEDIUM] Tratamento de erro genérico
**File:** `routes/task_routes.py:62`, `routes/task_routes.py:236`, `routes/user_routes.py:130`, `routes/user_routes.py:149`, `routes/report_routes.py:186`, `routes/report_routes.py:207`, `routes/report_routes.py:221`

**Description:** `except:` vazio repetido em quase todos os handlers, que engole a exceção sem log. Não existe error handler global.

**Impact:** Bugs reais ficam mascarados e as respostas de erro são inconsistentes.

**Recommendation:** Error handler central que registra o erro e devolve mensagem padrão (playbook #14).

### [LOW] APIs deprecated
**File:** `models/*.py`, `routes/*.py`, `services/notification_service.py:35`, `utils/helpers.py:38`, `seed.py`

**Description:** `datetime.utcnow()` aparece em dezenas de pontos e `Model.query.get(id)` em mais de 10 (por exemplo `task_routes.py:42`, `user_routes.py:29`, `report_routes.py:105`). Ambos são legados no Python 3.12+ e no SQLAlchemy 2.x.

**Impact:** Geram avisos de deprecation e podem quebrar em upgrades.

**Recommendation:** Trocar por `datetime.now(timezone.utc)` e `db.session.get(Model, id)` (playbook #17). Atenção: a mudança de datetime *aware* vs *naive* pode quebrar comparações com datas já gravadas.

### [LOW] Magic numbers e strings
**File:** `routes/task_routes.py:110`, `routes/task_routes.py:177`, `models/task.py:39`, `routes/user_routes.py:71`, `routes/user_routes.py:120`, `routes/user_routes.py:64`, `utils/helpers.py:110-116`

**Description:** Listas de status e roles e os limites de prioridade (1-5), título (3-200) e senha (4) estão escritos no código. As constantes de `helpers.py:110-116` existem mas ninguém as usa.

**Impact:** Mudar uma regra exige caçar vários pontos, com risco de valores inconsistentes.

**Recommendation:** Centralizar em `config/constants.py` e usar em todos os pontos (playbook #18).

### [LOW] Nomes ruins e código morto
**File:** `app.py:7`, `routes/task_routes.py:6-7`, `routes/user_routes.py:5-6`, `routes/report_routes.py:6,8`, `utils/helpers.py:2-7`, `routes/task_routes.py:141`, `routes/task_routes.py:210`

**Description:** Imports sem uso (`os, sys, json, hashlib, math`), helpers mortos (`generate_id`, `sanitize_string`, `format_date`, `is_valid_color`), nomes crípticos (`t`, `u`, `p1..p5`, `cat`) e `type(tags) == list` em vez de `isinstance`.

**Impact:** O código fica ruidoso e mais difícil de entender e de alterar com segurança.

**Recommendation:** Remover o que não é usado, renomear identificadores internos e usar `isinstance` (playbook #19).

### [LOW] Logging por print e configuração fixa
**File:** `routes/task_routes.py:149,153,219,234`, `routes/user_routes.py:83,89,147`, `services/notification_service.py:21,24`, `utils/helpers.py:39`, `app.py:11`

**Description:** `print` no lugar de um logger, e URI do banco (`sqlite:///tasks.db`), host e porta escritos no código.

**Impact:** Os logs não têm nível nem formato, e é preciso editar o código para mudar de ambiente.

**Recommendation:** Usar `logging` e ler as configurações de variáveis de ambiente em `config/settings.py` (playbook #20).

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
