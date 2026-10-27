================================
PHASE 2: ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.22.1
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 5 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials

**File:** `utils.js:1-7`

**Description:** `config` guarda `dbPass`, `paymentGatewayKey` (`pk_live_...`) e `smtpUser` como strings literais versionadas no repositório.

**Impact:** Qualquer pessoa com acesso ao código obtém a chave real do gateway de pagamento; trocar o segredo exige alterar o código.

**Recommendation:** Ler os segredos de variáveis de ambiente em `config/` e falhar no boot se faltarem (playbook #2).

### [CRITICAL] Armazenamento inseguro de senha

**File:** `utils.js:17-23`, `AppManager.js:18`, `AppManager.js:68`

**Description:** `badCrypto` concatena trechos de base64 e corta em 10 caracteres (hash falso, sem salt, determinístico). Usuários sem senha recebem o default `"123456"` e o seed grava `'123'` em texto puro.

**Impact:** Senhas recuperáveis trivialmente; senhas diferentes podem gerar o mesmo hash; contas com senha padrão previsível.

**Recommendation:** Usar `crypto.scrypt` com salt (ou bcrypt) e rejeitar senha ausente (playbook #4).

### [CRITICAL] Exposição de dados sensíveis em log

**File:** `AppManager.js:45`

**Description:** O checkout faz `console.log` do número completo do cartão e da chave do gateway de pagamento.

**Impact:** Dados de cartão e segredo de produção ficam em logs legíveis (violação PCI/LGPD).

**Recommendation:** Remover cartão e chave dos logs; logar apenas identificadores não sensíveis (playbook #3).

### [CRITICAL] God Class / God Module

**File:** `AppManager.js:4-139`

**Description:** `AppManager` cria o banco, define o schema e o seed, registra todas as rotas e implementa checkout, relatório financeiro e exclusão de usuário.

**Impact:** Nenhuma parte pode ser testada ou alterada isoladamente; toda mudança afeta tudo.

**Recommendation:** Separar em `config/`, `models/`, `controllers/`, `routes/` e `services/`; `app.js` vira composition root (playbook #6).

### [HIGH] Regra de negócio na rota

**File:** `AppManager.js:28-78`

**Description:** O handler de checkout decide a aprovação do pagamento (`cc.startsWith("4")`), cria usuário, matrícula, pagamento e auditoria, tudo dentro da rota HTTP.

**Impact:** A regra não é testável sem subir o servidor e não pode ser reaproveitada.

**Recommendation:** Extrair para `CheckoutService` e deixar o controller só coordenar (playbook #7).

### [HIGH] Estado global mutável

**File:** `utils.js:9-15`, `utils.js:25`, `AppManager.js:7`

**Description:** `globalCache` e `totalRevenue` são variáveis de módulo exportadas e alteradas em runtime por `logAndCache`; a conexão do banco é criada dentro do construtor.

**Impact:** Dependências escondidas entre requisições, cache nunca limpo, testes dependentes da ordem.

**Recommendation:** Remover o cache/contador global (não é lido em lugar nenhum) e centralizar o banco em `database/` injetado nos models (playbook #8).

### [HIGH] Ausência de autenticação/autorização

**File:** `AppManager.js:80`, `AppManager.js:131`

**Description:** `GET /api/admin/financial-report` e `DELETE /api/users/:id` aceitam qualquer requisição, sem checagem de identidade ou papel.

**Impact:** Qualquer cliente lê receita e nomes de alunos ou apaga usuários.

**Recommendation:** Adicionar middleware de autenticação e checagem de papel admin nessas rotas (playbook #9).

### [HIGH] Acoplamento forte

**File:** `app.js:8-10`, `AppManager.js:7`

**Description:** `app.js` instancia `AppManager`, que cria seu próprio `sqlite3.Database` e importa `utils` diretamente; nada é injetado.

**Impact:** Impossível trocar o banco ou usar mocks em testes.

**Recommendation:** Montar as dependências no entry point e injetá-las por construtor (playbook #10).

### [MEDIUM] Query N+1

**File:** `AppManager.js:83-127`

**Description:** O relatório executa 1 query de cursos, 1 de matrículas por curso e 2 queries (usuário e pagamento) por matrícula.

**Impact:** O tempo de resposta cresce linearmente com o volume de matrículas.

**Recommendation:** Buscar tudo com `JOIN` em uma query e agrupar em memória (playbook #11).

### [MEDIUM] Operação multi-passo sem transação

**File:** `AppManager.js:50-63`, `AppManager.js:131-136`

**Description:** Matrícula, pagamento e auditoria são inseridos separadamente, sem transação. A exclusão de usuário deixa matrículas e pagamentos órfãos.

**Impact:** Falhas parciais deixam dados inconsistentes (matrícula sem pagamento, registros sujos).

**Recommendation:** Envolver os passos em `BEGIN/COMMIT/ROLLBACK` e remover dependentes na exclusão (playbook #15).

### [MEDIUM] Callback hell

**File:** `AppManager.js:37-77`, `AppManager.js:83-127`

**Description:** Callbacks do sqlite3 aninhados em até 6 níveis no checkout e no relatório, com contadores manuais (`coursesPending`, `enrPending`).

**Impact:** Código difícil de ler; erros em callbacks internos são ignorados (ex.: `enrollments.length` quebra se `err`).

**Recommendation:** Promisificar o acesso ao banco e usar `async/await` (playbook #16).

### [MEDIUM] Validação de entrada ausente

**File:** `AppManager.js:29-35`, `AppManager.js:132`

**Description:** O checkout só testa se os campos existem; não valida formato de e-mail, tipo de `c_id`, nem exige `pwd`. `:id` do DELETE não é validado.

**Impact:** Dados inválidos são gravados e usuários são criados com senha padrão.

**Recommendation:** Centralizar a validação em um módulo usado pelos controllers (playbook #13).

### [MEDIUM] Tratamento de erro genérico

**File:** `AppManager.js:57`, `AppManager.js:104-106`, `AppManager.js:133-135`

**Description:** Erros de `audit_logs`, usuário, pagamento e DELETE são ignorados; o DELETE sempre responde sucesso. Demais erros devolvem texto solto ("Erro DB").

**Impact:** Falhas reais ficam mascaradas e as respostas de erro são inconsistentes.

**Recommendation:** Criar middleware central de erros e propagar exceções via `async/await` (playbook #14).

### [LOW] Magic numbers e strings

**File:** `AppManager.js:46`, `AppManager.js:68`, `utils.js:19-22`

**Description:** `"PAID"`, `"DENIED"`, o prefixo `"4"`, a senha `"123456"` e os números `10000`/`10` aparecem soltos no código.

**Impact:** Mudar uma regra exige caçar literais; significado pouco claro.

**Recommendation:** Extrair para constantes nomeadas em `config/constants.js` (playbook #18).

### [LOW] Nomes ruins e código morto

**File:** `AppManager.js:29-33`, `AppManager.js:26`, `utils.js:9-10`, `AppManager.js:2`

**Description:** Variáveis `u`, `e`, `p`, `cid`, `cc`; `totalRevenue` importado e nunca usado; campos `dbUser`, `dbPass`, `smtpUser` sem uso.

**Impact:** Leitura difícil e ruído no código.

**Recommendation:** Renomear para nomes descritivos e remover o código morto (playbook #19).

### [LOW] Logging por console.log e configuração fixa

**File:** `app.js:13`, `AppManager.js:7`, `AppManager.js:45`, `utils.js:6`, `utils.js:13`

**Description:** Uso de `console.log` sem nível; porta `3000` e banco `:memory:` fixos no código.

**Impact:** Mudar de ambiente exige editar o código; logs sem formato.

**Recommendation:** Ler porta e caminho do banco de variáveis de ambiente com defaults e usar um logger simples (playbook #20).

================================
Total: 16 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
