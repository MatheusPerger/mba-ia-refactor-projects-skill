# Anti-patterns Catalog

Catálogo de anti-patterns que a Fase 02 utilizará como referência para analisar o código e identificar oportunidades de melhoria. O catálogo conterá sinais de detecção que poderão ser buscados no código, com o objetivo de manter a abordagem agnóstica à linguagem de programação utilizada.

## Definição de Severidades

- **CRITICAL**: Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).

- **HIGH**: Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).

- **MEDIUM**: Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).

- **LOW**: Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

## Tabela de resumo

| # | Anti-Pattern | Severidade | Descrição |
| - | ------------ | ---------- | --------- |
| 1 | SQL Injection | CRITICAL | Query montada concatenando entrada do usuário |
| 2 | Credenciais hardcoded | CRITICAL | Senhas, chaves e tokens escritos no código-fonte |
| 3 | Exposição de dados sensíveis | CRITICAL | Senha, hash, cartão ou segredo em respostas e logs |
| 4 | Armazenamento inseguro de senha | CRITICAL | Senha em texto puro ou com hash fraco (MD5, base64) |
| 5 | Endpoints admin ou debug expostos | CRITICAL | Rotas perigosas sem proteção e modo debug ligado |
| 6 | God Class / God Module | CRITICAL | Um arquivo concentra banco, regra de negócio e rotas |
| 7 | Regra de negócio no Controller/Rota | HIGH | Cálculos e decisões dentro do handler HTTP |
| 8 | Estado global mutável | HIGH | Conexão, cache ou contador em variável global |
| 9 | Ausência de autenticação/autorização | HIGH | Rotas sensíveis acessíveis a qualquer um |
| 10 | Acoplamento forte / responsabilidades misturadas | HIGH | Camadas se criam e se chamam direto, sem separação |
| 11 | Query N+1 | MEDIUM | Query dentro de loop |
| 12 | Código duplicado | MEDIUM | Mesma lógica copiada em vários lugares |
| 13 | Validação de entrada ausente ou inconsistente | MEDIUM | Dados entram sem checagem de tipo, formato ou faixa |
| 14 | Tratamento de erro genérico e vazamento | MEDIUM | `except` amplo, erro interno devolvido ao cliente |
| 15 | Operação multi-passo sem transação | MEDIUM | Várias escritas sem atomicidade |
| 16 | Callback hell | MEDIUM | Callbacks aninhados em vez de async/await |
| 17 | APIs deprecated | LOW | Uso de funções obsoletas |
| 18 | Magic numbers e strings | LOW | Valores soltos sem nome |
| 19 | Nomes ruins e código morto | LOW | Variáveis crípticas, imports e variáveis não usados |
| 20 | Logging por print e configuração fixa | LOW | `print`/`console.log` e valores de ambiente fixos |

## Anti-Patterns detalhados

### 1. SQL Injection

**Descrição:** Query SQL montada juntando texto com dados vindos do usuário (concatenação, f-string, template string). O banco não consegue separar o comando do dado.

**Por que CRITICAL?** Permite ler, alterar ou apagar todo o banco e burlar login.

**Impactos**:

- Vazamento ou perda total dos dados
- Bypass de autenticação (`' OR '1'='1`)
- Comprometimento do servidor de banco

**Como detectar:**

- `execute`/`query`/`run` recebendo `"..." + var`, `f"...{var}"` ou `` `...${var}` ``
- `str()`/`format()`/`%s` aplicado dentro do texto do SQL
- Ausência de `?`, `%s` (parametrizado) ou `:nome` junto com valores de entrada

**Recomendação:** Usar queries parametrizadas (`execute(sql, params)`) ou o ORM. Nunca montar SQL com texto vindo de fora.

### 2. Credenciais hardcoded

**Descrição:** Senhas, chaves secretas, tokens e usuários de serviços escritos direto no código-fonte, e por isso versionados.

**Por que CRITICAL?** Quem tem acesso ao repositório ganha acesso aos sistemas reais.

**Impactos**:

- Segredos vazados em Git, logs e builds
- Impossível trocar a chave sem alterar o código
- Mesmo segredo em todos os ambientes

**Como detectar:**

- Variáveis com nome `secret`, `password`, `pass`, `token`, `api_key`, `smtp` recebendo string literal
- Prefixos de chave conhecidos (`pk_live_`, `sk_`, `AKIA`)
- Strings de conexão com usuário e senha no código

**Recomendação:** Mover para variáveis de ambiente lidas em um módulo de config. Falhar no boot se o segredo obrigatório não existir.

### 3. Exposição de dados sensíveis

**Descrição:** A aplicação devolve ou grava em log dados que não deveriam sair: senha, hash, número de cartão, chave secreta, caminho do banco.

**Por que CRITICAL?** Vaza dados de usuários e segredos a qualquer cliente ou a quem lê os logs.

**Impactos**:

- Roubo de contas e de dados de pagamento
- Violação de LGPD/PCI
- Segredos de infraestrutura revelados

**Como detectar:**

- `to_dict()`/serializador que inclui `password`, `senha`, `hash`
- `print`/`console.log` com cartão, token ou chave
- Rota de health/debug que retorna config (`secret_key`, `db_path`)

**Recomendação:** Criar serializadores com lista explícita de campos públicos. Remover segredos de logs e respostas.

### 4. Armazenamento inseguro de senha

**Descrição:** Senha guardada em texto puro ou protegida com algoritmo fraco ou falso (MD5, SHA1 sem salt, base64 repetido).

**Por que CRITICAL?** Um vazamento do banco revela as senhas rapidamente.

**Impactos**:

- Senhas recuperáveis por rainbow table ou força bruta
- Contas de outros sistemas comprometidas (reuso de senha)
- Senha padrão previsível (`123456`)

**Como detectar:**

- `md5`, `sha1`, `base64`, `btoa` aplicados a senha
- Coluna `senha`/`password` preenchida direto com o valor recebido
- Comparação `senha == valor_do_banco`

**Recomendação:** Usar hash com salt e custo (bcrypt, argon2 ou `werkzeug.security`). Comparar com a função de verificação da biblioteca.

### 5. Endpoints admin ou debug expostos

**Descrição:** Rotas que executam SQL livre, apagam dados ou resetam o banco sem proteção, e servidor rodando com `debug=True` em todas as interfaces.

**Por que CRITICAL?** Dá controle total do sistema, inclusive execução remota de código, a qualquer requisição.

**Impactos**:

- Perda ou alteração irreversível dos dados
- Execução remota de código pelo debugger
- Qualquer cliente vira administrador

**Como detectar:**

- Rotas `/admin/*`, `/reset`, `/query` sem checagem de identidade
- `debug=True`, `DEBUG = True`, `host='0.0.0.0'` fixos
- Handler que executa SQL ou comando vindo do body

**Recomendação:** Remover rotas de execução livre. Proteger as administrativas com autenticação e papel. Ler `debug` e `host` da config, desligado por padrão.

### 6. God Class / God Module

**Descrição:** Um único arquivo ou classe cuida de banco, regras de negócio, validação, rotas e formatação de vários domínios.

**Por que CRITICAL?** Viola por completo a separação de responsabilidades, e nada pode ser alterado ou testado isolado.

**Impactos**:

- Qualquer mudança afeta tudo
- Impossível testar em isolamento
- Conflitos constantes entre quem edita o arquivo

**Como detectar:**

- Arquivo ou classe grande (~200+ linhas) com SQL, regra de negócio e rotas juntos
- Um módulo que lida com 3 ou mais entidades diferentes (produto, usuário, pedido)
- Classe que cria o banco, registra rotas e processa pagamento

**Recomendação:** Dividir por domínio em Model, Controller e Rotas. Deixar o entry point só como composition root.

### 7. Regra de negócio no Controller/Model

**Descrição:** Cálculos, decisões e fluxos do negócio (checkout, desconto, relatório) escritos dentro do handler HTTP ou de camadas de persistência.

**Por que HIGH?** Mistura HTTP com negócio e impede reuso e teste, mas não expõe dados sozinho.

**Impactos**:

- Regra não pode ser testada sem subir o servidor
- Lógica copiada entre rotas
- Controllers longos e difíceis de ler
- Models com responsábilidades demais

**Como detectar:**

- Handler com muitos `if`, laços e cálculos sobre preço, estoque ou status
- Handler que acessa o banco direto
- Pasta `services/` existente mas sem uso pelas rotas
- Em models, método save() ou create() que executa regras não relacionadas à persistência (calcular imposto, escolher gateway de pagamento).

**Recomendação:** A saída é uma camada de service para regras que não pertencem nem ao model (dados puros) nem ao controller (fluxo HTTP).

### 8. Estado global mutável

**Descrição:** Conexão de banco, cache ou contadores guardados em variáveis globais que o código altera em runtime.

**Por que HIGH?** Cria dependências escondidas e comportamento imprevisível entre requisições.

**Impactos**:

- Bugs de concorrência (`check_same_thread=False`)
- Testes dependem da ordem de execução
- Difícil trocar o banco ou isolar um teste

**Como detectar:**

- Variável no topo do módulo atribuída e alterada dentro de funções (`global x`)
- Função `get_db()` que cria schema e seed a cada chamada
- Cache ou total exportado como variável de módulo

**Recomendação:** Centralizar a conexão em um módulo de database e injetá-la nos Models. Remover caches e contadores globais ou encapsulá-los em um objeto.

### 9. Ausência de autenticação/autorização

**Descrição:** Rotas sensíveis (criar admin, apagar usuário, relatórios, rotas admin) aceitam qualquer requisição. Login que devolve token falso também entra aqui.

**Por que HIGH?** Qualquer cliente executa ações privilegiadas, mas a falha é de controle de acesso, não de vazamento direto.

**Impactos**:

- Qualquer pessoa cria admin ou apaga dados
- Relatórios e dados privados abertos
- Token falso dá falsa sensação de segurança

**Como detectar:**

- Nenhum middleware, decorator ou guard de auth nas rotas
- `role` aceito direto do body
- Token montado por concatenação (`'fake-jwt-token-' + id`)

**Recomendação:** Adicionar um middleware de autenticação real (JWT ou sessão) e checagem de papel nas rotas sensíveis. Ignorar `role` vindo do cliente.

### 10. Acoplamento forte / responsabilidades misturadas

**Descrição:** Camadas e módulos se conhecem demais: criam suas dependências por dentro (`new X()`, import direto) e um arquivo reúne rotas de assuntos sem relação.

**Por que HIGH?** Viola SOLID (SRP e DIP) e bloqueia a troca ou teste de qualquer peça.

**Impactos**:

- Troca de banco ou serviço exige mexer em vários arquivos
- Não dá para usar mocks nos testes
- Blueprints e módulos com assuntos misturados

**Como detectar:**

- Rota chamando Model com SQL, ou Controller abrindo conexão
- Dependência criada dentro da função, sem receber por parâmetro
- Um blueprint/router com rotas de domínios diferentes (relatórios + categorias)

**Recomendação:** Receber as dependências por parâmetro ou construtor (injeção de dependência). Separar rotas por domínio e montar tudo no entry point.

### 11. Query N+1

**Descrição:** Uma query inicial seguida de uma query extra para cada item do resultado, dentro de um laço.

**Por que MEDIUM?** Piora a performance conforme os dados crescem, mas o sistema continua correto.

**Impactos**:

- Lentidão que cresce com o volume
- Sobrecarga no banco
- Respostas demoradas em listagens e relatórios

**Como detectar:**

- `execute`/`query`/`get` dentro de `for`/`while`/`map`
- `Model.query.get(x.id)` ou `len(obj.relacao)` em cada iteração
- Callbacks de query aninhados por item

**Recomendação:** Buscar tudo com `JOIN` ou carregamento em lote (`IN (...)`, `joinedload`) e montar o resultado em memória.

### 12. Código duplicado

**Descrição:** A mesma lógica (validação, cálculo, serialização) copiada em vários lugares em vez de ficar em uma função única.

**Por que MEDIUM?** Aumenta o custo de manutenção e o risco de divergência, sem quebrar o funcionamento.

**Impactos**:

- Correção feita em um lugar e esquecida nos outros
- Comportamentos inconsistentes
- Mais código para ler e testar

**Como detectar:**

- Blocos quase idênticos em 3 ou mais pontos
- Conversão de linha para dict repetida manualmente
- Método utilitário existente (`is_overdue`, `to_dict`) ignorado

**Recomendação:** Extrair para uma função, método de Model ou helper e reutilizar. Usar as constantes e métodos que já existem.

### 13. Validação de entrada ausente ou inconsistente

**Descrição:** Dados da requisição entram sem checar tipo, formato, faixa ou nulos, ou cada rota valida de um jeito.

**Por que MEDIUM?** Gera erros 500 e dados inválidos, mas costuma ser corrigível localmente.

**Impactos**:

- Erros 500 com entrada inesperada (`int("abc")`, body nulo)
- Dados inválidos gravados no banco
- Regras diferentes entre criar e atualizar

**Como detectar:**

- Conversão (`int()`, `parseInt`) sem tratamento de erro
- Leitura de `request.json` sem checar `None`
- Função de validação existente, mas não usada

**Recomendação:** Centralizar a validação em um módulo ou schema (ex: marshmallow) e usá-la em todas as rotas de escrita.

### 14. Tratamento de erro genérico e vazamento

**Descrição:** `try/except` amplo (ou `except:` vazio) repetido nas rotas, que engole o erro ou devolve a mensagem interna ao cliente.

**Por que MEDIUM?** Esconde falhas e vaza detalhes internos, sem derrubar a aplicação.

**Impactos**:

- Bugs reais mascarados
- Mensagens internas (`str(e)`) visíveis ao cliente
- Respostas de erro diferentes em cada rota

**Como detectar:**

- `except:` ou `except Exception` seguido de `str(e)` na resposta
- Mesmo bloco try/catch repetido em quase todos os handlers
- Ausência de error handler / middleware de erro global

**Recomendação:** Criar um error handler central que registra o erro e devolve uma mensagem padrão. Tratar só exceções conhecidas nas rotas.

### 15. Operação multi-passo sem transação

**Descrição:** Várias escritas dependentes (matrícula + pagamento + log, pedido + estoque) feitas separadas, sem transação.

**Por que MEDIUM?** Uma falha no meio deixa dados inconsistentes, mas é um risco pontual de integridade.

**Impactos**:

- Dados órfãos ou parciais
- Estoque errado após falha ou cancelamento
- Corrida entre requisições simultâneas

**Como detectar:**

- Vários `INSERT`/`UPDATE` seguidos sem `BEGIN`/`commit`/`rollback` em volta
- Erro de um passo ignorado e o fluxo continua
- Cancelar ou apagar sem desfazer efeitos (estoque, filhos)

**Recomendação:** Agrupar os passos em uma transação com commit no fim e rollback em erro. Tratar a remoção de dependentes.

### 16. Callback hell

**Descrição:** Callbacks aninhados em vários níveis para fluxos assíncronos, em vez de async/await ou Promises.

**Por que MEDIUM?** Dificulta a leitura e esconde erros ignorados, mas o fluxo funciona.

**Impactos**:

- Código difícil de seguir e alterar
- Erros dos callbacks internos ignorados
- Tratamento de erro repetido em cada nível

**Como detectar:**

- Funções anônimas aninhadas 3 ou mais níveis (`db.get(..., (err, x) => { db.run(...) })`)
- Parâmetro `err` não verificado
- Ausência de `async`/`await`/`Promise`

**Recomendação:** Converter para Promises (ex: `util.promisify` ou wrapper) e usar `async/await` com `try/catch`.

### 17. APIs deprecated

**Descrição:** Uso de funções, classes ou opções marcadas como obsoletas ou removidas, que têm um equivalente moderno.

**Por que LOW?** Ainda funciona hoje, mas gera avisos e pode quebrar em upgrades.

**Impactos**:

- Quebra em atualização de versão
- Avisos de deprecation nos logs
- Pior suporte e segurança

**Como detectar:**

- Comparar com a tabela abaixo
- Avisos `DeprecationWarning` ao rodar a aplicação
- Funções citadas como "legacy" na doc da versão do framework

**Recomendação:** Trocar pelo equivalente da tabela e conferir a versão do framework antes de alterar.

| Stack | API obsoleta | Equivalente moderno |
|---|---|---|
| Python | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| SQLAlchemy 2.x | `Model.query.get(id)` | `db.session.get(Model, id)` |
| SQLAlchemy 2.x | `Model.query.filter(...)` (estilo legado) | `db.session.execute(select(Model).where(...))` |
| Flask 2.3+ | `@app.before_first_request` | Executar o setup no boot, dentro de `app.app_context()` |
| Flask 2.3+ | `flask.json.JSONEncoder` | `app.json` (provider) |
| Node.js | `new Buffer(x)` | `Buffer.from(x)` / `Buffer.alloc(n)` |
| Node.js | `crypto.createCipher` | `crypto.createCipheriv` |
| Node.js | `fs.exists` | `fs.access` / `fs.promises.access` |
| Node.js | `url.parse()` | `new URL()` |
| Express 4 | `req.param('x')` | `req.params.x`, `req.query.x` ou `req.body.x` |
| Express 4 | `res.json(status, obj)` | `res.status(status).json(obj)` |
| Express 4 | `body-parser` separado | `express.json()` / `express.urlencoded()` |
| JavaScript | `var` | `let` / `const` |

### 18. Magic numbers e strings

**Descrição:** Números e textos com significado de negócio escritos soltos no código, sem nome.

**Por que LOW?** Prejudica a legibilidade, mas não afeta o funcionamento.

**Impactos**:

- Ninguém sabe o que o valor significa
- Mudar a regra exige caçar o valor
- Valores repetidos e inconsistentes

**Como detectar:**

- Literais numéricos em `if`/cálculos (`> 10000`, `0.1`, `substring(0, 10)`)
- Listas de status, categorias e papéis escritas dentro das rotas
- Constantes existentes, mas não usadas

**Recomendação:** Extrair para constantes nomeadas ou enums em um módulo de config/constantes e usar em todos os pontos.

### 19. Nomes ruins e código morto

**Descrição:** Variáveis com nomes curtos ou crípticos (`u`, `e`, `cid`), e imports ou variáveis que nunca são usados.

**Por que LOW?** É um problema de legibilidade, sem impacto direto no comportamento.

**Impactos**:

- Código difícil de entender
- Ruído e imports desnecessários
- Maior chance de erro em mudanças

**Como detectar:**

- Nomes de 1 a 3 letras fora de laços simples
- Import ou variável sem nenhuma referência
- Comparação por tipo (`type(x) == list`) em vez de `isinstance`

**Recomendação:** Renomear para nomes que dizem o que são e remover imports e variáveis não usados.

### 20. Logging por print e configuração fixa

**Descrição:** Uso de `print`/`console.log` no lugar de um logger, e valores de ambiente (porta, URI do banco, host) escritos no código.

**Por que LOW?** Dificulta operação e deploy, mas não quebra o funcionamento.

**Impactos**:

- Logs sem nível, data ou formato
- Precisa editar o código para mudar de ambiente
- Banco em memória e porta fixos por engano

**Como detectar:**

- `print(` / `console.log(` nas rotas e models
- Porta, host e URI de banco como literal
- Ausência de módulo de config e de `.env`

**Recomendação:** Usar o módulo de logging da linguagem e ler porta, host e URI de variáveis de ambiente com valores padrão em um módulo de config.
