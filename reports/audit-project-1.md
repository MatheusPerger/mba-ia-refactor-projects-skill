================================
PHASE 2: ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 6 | HIGH: 4 | MEDIUM: 5 | LOW: 3

## Findings

### [CRITICAL] SQL Injection

**File:** models.py:28, models.py:48-50, models.py:58-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-166, models.py:174, models.py:188, models.py:192, models.py:206-224, models.py:279-281, models.py:289-297

**Description:** Todas as queries são montadas concatenando texto vindo do request (`"... '" + email + "'"`). O banco não separa comando de dado.

**Impact:** Qualquer pessoa burla o login (`' OR '1'='1`), lê, altera ou apaga todo o banco.

**Recommendation:** Usar queries parametrizadas com `?` (playbook, seção 1).

### [CRITICAL] Credenciais hardcoded

**File:** app.py:7, controllers.py:289

**Description:** `SECRET_KEY` fixa como `"minha-chave-super-secreta-123"` no código e repetida na resposta do `/health`.

**Impact:** Quem acessa o repositório conhece a chave; ela não pode ser trocada sem alterar o código e é igual em todos os ambientes.

**Recommendation:** Ler de variável de ambiente em `config/settings.py` e falhar no boot se não existir (playbook, seção 2).

### [CRITICAL] Exposição de dados sensíveis

**File:** models.py:83, models.py:99, controllers.py:285-289

**Description:** `GET /usuarios` e `GET /usuarios/<id>` devolvem a coluna `senha`. O `/health` devolve `secret_key`, `db_path` e `debug`.

**Impact:** Qualquer cliente obtém as senhas de todos os usuários e a chave da aplicação.

**Recommendation:** Serializador com lista explícita de campos públicos e `/health` sem config (playbook, seção 3).

### [CRITICAL] Armazenamento inseguro de senha

**File:** models.py:110, models.py:128, database.py:76-78

**Description:** Senha gravada em texto puro e comparada direto no SQL (`senha = '...'`). O seed usa senhas previsíveis (`admin123`, `123456`).

**Impact:** Um vazamento do banco expõe todas as senhas imediatamente.

**Recommendation:** Hash com salt via `werkzeug.security`; buscar por e-mail e verificar o hash (playbook, seção 4).

### [CRITICAL] Endpoints admin e debug expostos

**File:** app.py:8, app.py:47-57, app.py:59-78, app.py:88

**Description:** `/admin/reset-db` apaga todas as tabelas e `/admin/query` executa SQL arbitrário do body, ambos sem autenticação. `debug=True` com `host="0.0.0.0"` fixos.

**Impact:** Qualquer requisição apaga ou altera o banco; o debugger do Werkzeug permite execução remota de código.

**Recommendation:** Remover `/admin/query`, proteger `/admin/reset-db` com auth/papel e ler `debug`/`host` da config, desligado por padrão (playbook, seção 5).

### [CRITICAL] God Module

**File:** models.py:1-314, controllers.py:1-292, app.py:1-88

**Description:** `models.py` junta SQL, regra de negócio e formatação de 4 domínios (produtos, usuários, pedidos, relatórios); `controllers.py` faz o mesmo no HTTP; `app.py` mistura rotas, SQL e endpoints admin.

**Impact:** Qualquer mudança afeta tudo; impossível testar uma parte isolada.

**Recommendation:** Dividir por domínio em models, controllers e routes; `app.py` só como composition root (playbook, seção 6).

### [HIGH] Regra de negócio no Controller/Model

**File:** models.py:133-169, models.py:256-262, controllers.py:43-54, controllers.py:208-210, controllers.py:247-250

**Description:** Cálculo de total, checagem de estoque e faixas de desconto do relatório estão no model; validação de produto e "notificações" de pedido estão nos handlers.

**Impact:** Regras não podem ser testadas sem banco/servidor e ficam espalhadas entre camadas.

**Recommendation:** Extrair para services (pedido, relatório) usados pelos controllers (playbook, seção 7).

### [HIGH] Estado global mutável

**File:** database.py:4-12, database.py:54-84

**Description:** `db_connection` é global, reaproveitada entre requisições com `check_same_thread=False`; `get_db()` também cria schema e seed.

**Impact:** Conexão compartilhada entre threads (risco de concorrência) e setup misturado com acesso a dados.

**Recommendation:** `init_db()` no boot e conexão por requisição via `g`, fechada no teardown (playbook, seção 8).

### [HIGH] Ausência de autenticação/autorização

**File:** app.py:11-30, app.py:47-59, controllers.py:167-186

**Description:** Nenhuma rota exige identidade: qualquer um lista usuários, cria/apaga produtos, altera status de pedidos e vê relatórios. O `/login` não devolve token.

**Impact:** Qualquer cliente executa ações privilegiadas.

**Recommendation:** Middleware de auth com token assinado e checagem de papel nas rotas sensíveis (playbook, seção 9).

### [HIGH] Acoplamento forte / responsabilidades misturadas

**File:** controllers.py:3, controllers.py:264-292, app.py:47-78

**Description:** `health_check` e as rotas admin abrem a conexão e executam SQL direto, fora de qualquer model; as dependências são importadas diretamente, sem injeção.

**Impact:** Troca de banco ou testes com mock exigem mexer em vários arquivos.

**Recommendation:** Mover o SQL para models e receber dependências por parâmetro (playbook, seção 10).

### [MEDIUM] Query N+1

**File:** models.py:171-201, models.py:203-233, models.py:139-146, models.py:154-166

**Description:** Listagens de pedidos fazem uma query de itens por pedido e uma de produto por item; `criar_pedido` consulta produto dentro de dois laços.

**Impact:** Lentidão e carga no banco crescem com o volume de pedidos.

**Recommendation:** `JOIN` ou carregamento em lote com `IN (...)` (playbook, seção 11).

### [MEDIUM] Código duplicado

**File:** models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, models.py:178-199, models.py:211-231, controllers.py:30-50, controllers.py:74-90

**Description:** Conversão de linha para dict repetida 3x (produto), 2x (usuário) e 2x (pedido); validação de produto copiada em criar e atualizar.

**Impact:** Correções esquecidas em uma das cópias.

**Recommendation:** Helpers de serialização nos models e validação única (playbook, seções 12 e 13).

### [MEDIUM] Validação de entrada ausente ou inconsistente

**File:** controllers.py:43-45, controllers.py:72-93, controllers.py:118-121, controllers.py:169-171, controllers.py:195-203, controllers.py:239-240

**Description:** `preco < 0` com valor não numérico, `float()` em query string, `dados.get` com body nulo no login/status e itens do pedido sem checar tipo/quantidade geram erro 500. O update não valida nome nem categoria como o create.

**Impact:** Erros 500 com entrada inesperada e dados inválidos gravados.

**Recommendation:** Validação centralizada reutilizada em criar e atualizar, retornando 400 (playbook, seção 13).

### [MEDIUM] Tratamento de erro genérico e vazamento

**File:** controllers.py:10-12, controllers.py:21-22, controllers.py:60-62, controllers.py:95-96, controllers.py:108-109, controllers.py:125-126, controllers.py:218-220, controllers.py:254-255, controllers.py:291-292, app.py:77-78

**Description:** `try/except Exception` repetido em todos os handlers devolvendo `str(e)` ao cliente.

**Impact:** Mensagens internas vazam e bugs ficam mascarados.

**Recommendation:** Error handler global que loga e devolve mensagem padrão (playbook, seção 14).

### [MEDIUM] Operação multi-passo sem transação

**File:** models.py:133-169, controllers.py:247-250

**Description:** `criar_pedido` insere pedido, itens e baixa estoque sem rollback em caso de erro, e o estoque é verificado fora da escrita. Cancelar pedido não devolve o estoque.

**Impact:** Pedidos parciais, estoque incorreto e vendas acima do estoque em requisições simultâneas.

**Recommendation:** Transação com commit/rollback e `UPDATE ... AND estoque >= ?` (playbook, seção 15).

### [LOW] Magic numbers e strings

**File:** controllers.py:52, controllers.py:242, models.py:256-262, database.py:5

**Description:** Categorias válidas, status de pedido e faixas de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) escritos soltos no código.

**Impact:** Mudar uma regra exige caçar o valor.

**Recommendation:** Constantes nomeadas em `config/constants.py` (playbook, seção 18).

### [LOW] Logging por print e configuração fixa

**File:** controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:208-210, controllers.py:248-250, app.py:56, app.py:83-88, database.py:5

**Description:** `print` no lugar de logger; porta, host, debug e caminho do banco fixos no código.

**Impact:** Logs sem nível/formato e necessidade de editar código para mudar de ambiente.

**Recommendation:** `logging` e `config/settings.py` com variáveis de ambiente (playbook, seção 20).

### [LOW] Nomes ruins e código morto

**File:** models.py:2, database.py:2, models.py:187, models.py:191, controllers.py:14

**Description:** `import sqlite3` (models) e `import os` (database) sem uso; `cursor2`/`cursor3`; parâmetro `id` sombreia o builtin.

**Impact:** Ruído e leitura mais difícil.

**Recommendation:** Remover imports e renomear identificadores internos (playbook, seção 19).

================================
Total: 18 findings
================================
