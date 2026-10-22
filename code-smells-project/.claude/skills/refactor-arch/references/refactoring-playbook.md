# Refactoring Playbook

Conjunto de soluções práticas para corrigir os anti-patterns identificados na Fase 2. Cada solução deve conter:

- **Critérios de aplicação:** situações que indicam quando a solução deve ser utilizada.
- **Exemplo de código antes e depois:** demonstração em pelo menos uma linguagem, com a sintaxe adaptada à stack do projeto, mantendo o conceito independente da tecnologia.
- **Pontos de atenção:** possíveis problemas ou efeitos colaterais decorrentes de uma aplicação inadequada.

Para simplificar a apresentação, os exemplos alternam entre Python e JavaScript. Em outras stacks, como Go, Ruby e Java, os mesmos princípios podem ser aplicados, respeitando as particularidades de cada linguagem: extrair responsabilidades, parametrizar comportamentos e isolar componentes.

## Sumário

**Segurança**

1. [SQL Injection → Queries parametrizadas](#1-sql-injection--queries-parametrizadas)
2. [Credenciais hardcoded → Config via variáveis de ambiente](#2-credenciais-hardcoded--config-via-variáveis-de-ambiente)
3. [Exposição de dados sensíveis → Serializador com lista explícita de campos](#3-exposição-de-dados-sensíveis--serializador-com-lista-explícita-de-campos)
4. [Armazenamento inseguro de senha → Hash com salt e custo](#4-armazenamento-inseguro-de-senha--hash-com-salt-e-custo)
5. [Endpoints admin ou debug expostos → Remover rotas perigosas e desligar debug](#5-endpoints-admin-ou-debug-expostos--remover-rotas-perigosas-e-desligar-debug)

**Arquitetura**

6. [God Class / God Module → Dividir em Model, Controller e Rotas](#6-god-class--god-module--dividir-em-model-controller-e-rotas)
7. [Regra de negócio no Controller/Model → Camada de Service](#7-regra-de-negócio-no-controllermodel--camada-de-service)
8. [Estado global mutável → Módulo de database e injeção](#8-estado-global-mutável--módulo-de-database-e-injeção)
9. [Ausência de autenticação/autorização → Middleware de auth e papéis](#9-ausência-de-autenticaçãoautorização--middleware-de-auth-e-papéis)
10. [Acoplamento forte → Injeção de dependência](#10-acoplamento-forte--injeção-de-dependência)

**Robustez e qualidade**

11. [Query N+1 → JOIN ou carregamento em lote](#11-query-n1--join-ou-carregamento-em-lote)
12. [Código duplicado → Função/helper único](#12-código-duplicado--funçãohelper-único)
13. [Validação de entrada ausente ou inconsistente → Validação centralizada](#13-validação-de-entrada-ausente-ou-inconsistente--validação-centralizada)
14. [Tratamento de erro genérico → Error handler central](#14-tratamento-de-erro-genérico--error-handler-central)
15. [Operação multi-passo sem transação → Transação com commit/rollback](#15-operação-multi-passo-sem-transação--transação-com-commitrollback)
16. [Callback hell → Promises e async/await](#16-callback-hell--promises-e-asyncawait)
17. [APIs deprecated → Equivalente moderno](#17-apis-deprecated--equivalente-moderno)
18. [Magic numbers e strings → Constantes nomeadas](#18-magic-numbers-e-strings--constantes-nomeadas)
19. [Nomes ruins e código morto → Renomear e remover](#19-nomes-ruins-e-código-morto--renomear-e-remover)
20. [Logging por print e configuração fixa → Logger e módulo de config](#20-logging-por-print-e-configuração-fixa--logger-e-módulo-de-config)

**Ordem de aplicação**

- [Priorização recomendada](#priorização-recomendada)

---

## 1. SQL Injection → Queries parametrizadas

**Quanto aplicar:** Sempre que um `execute`/`query`/`run` receber SQL montado com concatenação, f-string ou template string contendo dado vindo de fora.

**Antes:**

```python
cursor.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")
```

**Depois:**

```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```

**Transformação:**

- SQL montado com f-string substituído por query com placeholder `?`
- O valor do usuário passa como parâmetro separado do comando
- O driver faz o escape, então o dado nunca vira SQL

**Pontos de atenção:**

- O placeholder depende do driver: `?` (sqlite3), `%s` (psycopg2, MySQL), `:nome` (SQLAlchemy).
- Nome de tabela, coluna e `ORDER BY` não aceitam parâmetro; valide contra uma lista fixa.

---

## 2. Credenciais hardcoded → Config via variáveis de ambiente

**Quanto aplicar:** Quando houver senha, token, `SECRET_KEY` ou chave de API escritos como literal no código.

**Antes:**

```javascript
const JWT_SECRET = "segredo-fixo";
```

**Depois:**

```javascript
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) throw new Error("JWT_SECRET não definido");
```

**Transformação:**

- Segredo literal removido do código
- Valor lido de `process.env`
- Boot falha se a variável obrigatória não existir

**Pontos de atenção:**

- Criar um `.env.example` sem valores reais e manter `.env` no `.gitignore`.
- Segredos já commitados continuam no histórico do Git: avisar que precisam ser rotacionados.

---

## 3. Exposição de dados sensíveis → Serializador com lista explícita de campos

**Quanto aplicar:** Quando a resposta devolve o objeto inteiro (`to_dict()`, `SELECT *`) ou quando logs registram senha, cartão ou token.

**Antes:**

```python
return jsonify(usuario.__dict__)  # inclui senha_hash
```

**Depois:**

```python
return jsonify({"id": usuario.id, "nome": usuario.nome, "email": usuario.email})
```

**Transformação:**

- `__dict__` (todos os campos) trocado por dict explícito
- Só `id`, `nome` e `email` saem na resposta
- `senha_hash` deixa de ser exposto

**Pontos de atenção:**

- Use lista de campos **permitidos**; um campo novo no model não pode vazar por padrão.
- Revise também listagens e relatórios, que costumam ter serialização própria.

---

## 4. Armazenamento inseguro de senha → Hash com salt e custo

**Quanto aplicar:** Quando a senha é gravada em texto puro ou com MD5, SHA1 ou base64.

**Antes:**

```python
senha_hash = hashlib.md5(senha.encode()).hexdigest()
```

**Depois:**

```python
import bcrypt
senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
```

**Transformação:**

- MD5 (rápido e sem salt) trocado por bcrypt
- O salt é gerado a cada hash
- O custo do algoritmo dificulta força bruta

**Pontos de atenção:**

- Senhas já gravadas não podem ser convertidas: faça o rehash no próximo login ou force a redefinição.
- Confirme que a coluna comporta o tamanho do novo hash.

---

## 5. Endpoints admin ou debug expostos → Remover rotas perigosas e desligar debug

**Quanto aplicar:** Quando existir rota que executa SQL/comando vindo do body, `/reset` ou `/admin/*` sem proteção, ou `debug=True` fixo.

**Antes:**

```python
@app.route("/admin/query", methods=["POST"])
def admin_query():
    return jsonify(db.execute(request.json["sql"]).fetchall())

app.run(host="0.0.0.0", debug=True)
```

**Depois:**

```python
# rota de SQL livre removida
app.run(host=settings.HOST, debug=settings.DEBUG)  # DEBUG=false por padrão
```

**Transformação:**

- Rota de SQL livre removida
- `host` e `debug` passam a vir da config
- `DEBUG` desligado por padrão

**Pontos de atenção:**

- Rotas de execução livre devem ser removidas, não protegidas.
- As rotas administrativas que ficarem precisam de autenticação (seção 9).

---

## 6. God Class / God Module → Dividir em Model, Controller e Rotas

**Quanto aplicar:** Quando um único arquivo ou classe mistura SQL, regras de negócio e rotas de várias entidades.

**Antes:**

```python
# app.py
@app.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.json
    db.execute("INSERT INTO produtos (nome) VALUES (?)", (dados["nome"],))
    return jsonify({"ok": True})
# ... pedidos, usuários, relatórios no mesmo arquivo
```

**Depois:**

```python
# models/produto_model.py
def criar(nome):
    get_db().execute("INSERT INTO produtos (nome) VALUES (?)", (nome,))

# controllers/produto_controller.py
def criar_produto():
    produto_model.criar(request.get_json()["nome"])
    return jsonify({"ok": True}), 201

# app.py (só registra as rotas)
app.register_blueprint(produto_bp)
```

**Transformação:**

- Rota, SQL e resposta separados em model, controller e rota
- `app.py` só registra o blueprint
- Cada camada ganha uma única responsabilidade

**Pontos de atenção:**

- Refatore um domínio por vez e preserve URLs e formato das respostas.
- Evite imports circulares: rota → controller → model.

---

## 7. Regra de negócio no Controller/Model → Camada de Service

**Quanto aplicar:** Quando o handler HTTP tem cálculos e decisões de negócio (preço, desconto, estoque), ou o model executa regras que não são de persistência.

**Antes:**

```javascript
router.post("/pedido", (req, res) => {
  let total = 0;
  req.body.itens.forEach((i) => { total += i.preco * i.qtd; });
  if (total > 1000) total *= 0.9;
  db.run("INSERT INTO pedidos (total) VALUES (?)", [total]);
  res.json({ total });
});
```

**Depois:**

```javascript
// services/pedidoService.js
exports.criar = async (itens) => {
  const bruto = itens.reduce((soma, i) => soma + i.preco * i.qtd, 0);
  const total = bruto > 1000 ? bruto * 0.9 : bruto;
  return pedidoModel.criar(total);
};

// controllers/pedidoController.js
exports.criar = async (req, res, next) => {
  try { res.status(201).json(await pedidoService.criar(req.body.itens)); }
  catch (err) { next(err); }
};
```

**Transformação:**

- Cálculo de total e desconto movido do handler para o service
- Controller só chama o service e devolve o status HTTP
- Persistência isolada no model

**Pontos de atenção:**

- O service não conhece `req`/`res`; o controller só traduz HTTP.
- Não crie service que apenas repassa chamada ao model; use quando houver regra de fato.

---

## 8. Estado global mutável → Módulo de database e injeção

**Quanto aplicar:** Quando conexão, cache ou contador ficam em variável global alterada em runtime, ou `get_db()` recria schema/seed a cada chamada.

**Antes:**

```python
_conn = None

def get_db():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect("loja.db", check_same_thread=False)
        criar_tabelas(_conn)
    return _conn
```

**Depois:**

```python
# database.py
def init_db(path):
    with sqlite3.connect(path) as conn:
        criar_tabelas(conn)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_URI"])
    return g.db

# app.py
app.teardown_appcontext(lambda _exc: g.pop("db", None) and g.db.close())
```

**Transformação:**

- Variável global `_conn` removida
- Conexão obtida por requisição via `g` e fechada no teardown
- Criação do schema movida para `init_db` no boot

**Pontos de atenção:**

- Criação de schema e seed acontece uma vez no boot, nunca dentro de `get_db()`.
- Contadores e caches globais: remova se puderem ser calculados a partir do banco.

---

## 9. Ausência de autenticação/autorização → Middleware de auth e papéis

**Quanto aplicar:** Quando rotas sensíveis (apagar, criar admin, relatórios) aceitam qualquer requisição, ou o `role` vem do body.

**Antes:**

```javascript
app.delete("/usuarios/:id", usuarioController.apagar);
```

**Depois:**

```javascript
function authenticate(req, res, next) {
  try {
    req.user = jwt.verify((req.headers.authorization || "").replace("Bearer ", ""), JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ erro: "Não autenticado" });
  }
}

const requireRole = (role) => (req, res, next) =>
  req.user.role === role ? next() : res.status(403).json({ erro: "Sem permissão" });

app.delete("/usuarios/:id", authenticate, requireRole("admin"), usuarioController.apagar);
```

**Transformação:**

- Middleware `authenticate` valida o token JWT
- `requireRole` checa o papel e devolve 403
- Rota passa a declarar a proteção exigida

**Pontos de atenção:**

- Ignore o `role` enviado pelo cliente; o papel é definido no servidor.
- A mudança afeta clientes existentes; defina quais rotas continuam públicas (login, cadastro).

---

## 10. Acoplamento forte → Injeção de dependência

**Quanto aplicar:** Quando uma camada cria suas dependências por dentro (`new X()`, conexão aberta no controller) ou um router mistura domínios.

**Antes:**

```python
class PedidoController:
    def __init__(self):
        self.db = sqlite3.connect("loja.db")
```

**Depois:**

```python
class PedidoController:
    def __init__(self, pedido_service):
        self.pedido_service = pedido_service

# app.py (composition root)
controller = PedidoController(PedidoService(PedidoModel(get_db)))
```

**Transformação:**

- Controller deixa de abrir a conexão com o banco
- Dependência recebida pelo construtor
- Objetos montados num único ponto (composition root)

**Pontos de atenção:**

- Não precisa de framework de DI: passar por construtor ou parâmetro basta.
- A montagem fica toda no entry point; `new` dentro de controllers indica injeção incompleta.

---

## 11. Query N+1 → JOIN ou carregamento em lote

**Quanto aplicar:** Quando houver query dentro de `for`/`while`/`map`, principalmente em listagens e relatórios.

**Antes:**

```python
for pedido in pedidos:
    pedido["itens"] = db.execute(
        "SELECT * FROM itens WHERE pedido_id = ?", (pedido["id"],)
    ).fetchall()
```

**Depois:**

```python
ids = [p["id"] for p in pedidos]
marcas = ",".join("?" * len(ids))
itens = db.execute(f"SELECT * FROM itens WHERE pedido_id IN ({marcas})", ids).fetchall()

for pedido in pedidos:
    pedido["itens"] = [i for i in itens if i["pedido_id"] == pedido["id"]]
```

**Transformação:**

- Query dentro do laço trocada por uma única consulta com `IN`
- Itens agrupados em memória por `pedido_id`
- De N+1 queries para 2

**Pontos de atenção:**

- Trate lista vazia: `IN ()` é inválido em vários bancos.
- Com ORM, prefira `joinedload`/`selectinload` ou `include`.

---

## 12. Código duplicado → Função/helper único

**Quanto aplicar:** Quando o mesmo bloco (validação, cálculo, serialização) aparece em 3 ou mais pontos, ou um método utilitário existente é ignorado.

**Antes:**

```javascript
// repetido em várias rotas
if (!email || !email.includes("@")) return res.status(400).json({ erro: "E-mail inválido" });
```

**Depois:**

```javascript
// utils/validators.js
exports.emailValido = (email) => typeof email === "string" && email.includes("@");

// rotas
if (!emailValido(email)) return res.status(400).json({ erro: "E-mail inválido" });
```

**Transformação:**

- Validação repetida extraída para `emailValido`
- Rotas passam a chamar o helper
- Regra alterada em um só lugar

**Pontos de atenção:**

- Unifique apenas trechos iguais por razão de negócio, não por coincidência.
- Compare as cópias antes: pequenas diferenças podem ser comportamento intencional.

---

## 13. Validação de entrada ausente ou inconsistente → Validação centralizada

**Quanto aplicar:** Quando há `int()`/`parseInt` sem tratamento, `request.json` sem checar `None`, ou regras diferentes entre criar e atualizar.

**Antes:**

```python
dados = request.json
preco = float(dados["preco"])
```

**Depois:**

```python
def validar_produto(dados):
    if not isinstance(dados, dict) or not dados.get("nome"):
        raise ValidationError("nome é obrigatório")
    try:
        preco = float(dados["preco"])
    except (KeyError, TypeError, ValueError):
        raise ValidationError("preco deve ser numérico")
    if preco < 0:
        raise ValidationError("preco não pode ser negativo")
    return {"nome": dados["nome"], "preco": preco}

dados = validar_produto(request.get_json(silent=True))
```

**Transformação:**

- Conversão direta de `float()` encapsulada em `validar_produto`
- Entrada inválida gera `ValidationError` em vez de erro 500
- Mesma função reutilizável em criar e atualizar

**Pontos de atenção:**

- Falha de validação retorna `400`, nunca `500`.
- Use a mesma validação em criar e atualizar e mantenha o formato de erro já usado pela API.

---

## 14. Tratamento de erro genérico → Error handler central

**Quanto aplicar:** Quando `try/except` amplo se repete nas rotas, `str(e)` volta ao cliente, ou não há error handler global.

**Antes:**

```python
try:
    return jsonify(produto_model.buscar(id))
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```

**Depois:**

```python
@app.errorhandler(NotFoundError)
def handle_not_found(err):
    return jsonify({"erro": str(err)}), 404

@app.errorhandler(Exception)
def handle_unexpected(err):
    app.logger.exception("Erro inesperado")
    return jsonify({"erro": "Erro interno do servidor"}), 500

# controller, sem try/except
return jsonify(produto_model.buscar(id))
```

**Transformação:**

- `try/except` removido do controller
- Erros tratados em handlers globais por tipo
- Erro inesperado é logado e o cliente recebe mensagem genérica

**Pontos de atenção:**

- O erro real vai para o log; o cliente recebe só a mensagem padrão.
- No Express, o middleware de erro vem depois das rotas, tem 4 parâmetros, e handlers `async` precisam chamar `next(err)`.

---

## 15. Operação multi-passo sem transação → Transação com commit/rollback

**Quanto aplicar:** Quando várias escritas dependentes (pedido + itens + estoque) acontecem em sequência sem `commit`/`rollback` em volta.

**Antes:**

```python
db.execute("INSERT INTO pedidos (total) VALUES (?)", (total,))
db.execute("UPDATE produtos SET estoque = estoque - 1 WHERE id = ?", (produto_id,))
db.commit()
```

**Depois:**

```python
try:
    db.execute("INSERT INTO pedidos (total) VALUES (?)", (total,))
    db.execute(
        "UPDATE produtos SET estoque = estoque - 1 WHERE id = ? AND estoque >= 1",
        (produto_id,),
    )
    db.commit()
except Exception:
    db.rollback()
    raise
```

**Transformação:**

- Escritas agrupadas num bloco com `commit` e `rollback`
- Falha em qualquer passo desfaz tudo
- Estoque só baixa se houver quantidade suficiente

**Pontos de atenção:**

- A transação fica no service/model, não no controller.
- Efeitos externos (e-mail, pagamento) rodam depois do commit, pois não participam do rollback.

---

## 16. Callback hell → Promises e async/await

**Quanto aplicar:** Quando houver callbacks aninhados em 3 ou mais níveis ou o parâmetro `err` for ignorado.

**Antes:**

```javascript
db.get("SELECT * FROM usuarios WHERE id = ?", [id], (err, usuario) => {
  db.all("SELECT * FROM pedidos WHERE usuario_id = ?", [usuario.id], (err, pedidos) => {
    res.json({ usuario, pedidos });
  });
});
```

**Depois:**

```javascript
const get = promisify(db.get.bind(db));
const all = promisify(db.all.bind(db));

try {
  const usuario = await get("SELECT * FROM usuarios WHERE id = ?", [id]);
  const pedidos = await all("SELECT * FROM pedidos WHERE usuario_id = ?", [usuario.id]);
  res.json({ usuario, pedidos });
} catch (err) {
  next(err);
}
```

**Transformação:**

- Callbacks aninhados trocados por `await` sequencial
- `db.get`/`db.all` convertidos com `promisify`
- Erros tratados num único `try/catch`

**Pontos de atenção:**

- `promisify(db.run)` perde `this.lastID` e `this.changes` do sqlite3; use um wrapper se precisar deles.
- Converta o fluxo inteiro; misturar callbacks e `await` na mesma função mantém o problema.

---

## 17. APIs deprecated → Equivalente moderno

**Quanto aplicar:** Quando o código usa funções marcadas como obsoletas (veja a tabela do catálogo) ou a execução emite `DeprecationWarning`.

**Antes:**

```python
criado_em = datetime.utcnow()
produto = Produto.query.get(id)
```

**Depois:**

```python
criado_em = datetime.now(timezone.utc)
produto = db.session.get(Produto, id)
```

**Transformação:**

- `utcnow()` trocado por `now(timezone.utc)`
- `Query.get` trocado por `db.session.get`
- Mesmo comportamento, sem avisos de deprecation

**Pontos de atenção:**

- `datetime.now(timezone.utc)` é *aware*; compará-lo com datetimes *naive* já gravados gera `TypeError`.
- Confirme a versão instalada do framework antes de trocar.

---

## 18. Magic numbers e strings → Constantes nomeadas

**Quanto aplicar:** Quando houver literais com significado de negócio em `if` e cálculos, ou listas de status/papéis dentro das rotas.

**Antes:**

```python
if total > 10000:
    total *= 0.9
```

**Depois:**

```python
# config/constants.py
LIMITE_DESCONTO = 10000
PERCENTUAL_DESCONTO = 0.10

if total > LIMITE_DESCONTO:
    total *= 1 - PERCENTUAL_DESCONTO
```

**Transformação:**

- Números soltos substituídos por constantes nomeadas
- Valores com nomes que indicam o que representam
- Podem ser variaveis locais, de classe ou constantes centralizadas (quando existem usos de varios arquivos)

**Pontos de atenção:**

- `0`, `1` e `-1` óbvios podem ficar como estão.
- Valores que mudam por ambiente (porta, URL) vão para a config (seção 20), não para constantes.

---

## 19. Nomes ruins e código morto → Renomear e remover

**Quanto aplicar:** Quando houver variáveis crípticas (`u`, `e`, `cid`), imports ou variáveis sem uso, ou comparação por tipo (`type(x) == list`).

**Antes:**

```javascript
const fs = require("fs");
function calc(a, b) { return a * b; }
```

**Depois:**

```javascript
function calcularSubtotal(preco, quantidade) { return preco * quantidade; }
```

**Transformação:**

- Nomes genéricos (`calc`, `a`, `b`) renomeados
- Import `fs` sem uso removido
- O nome da função descreve o que ela faz

**Pontos de atenção:**

- Renomear campos de API ou colunas do banco muda o contrato; renomeie só identificadores internos.
- Antes de remover um import, busque uso global: pode ter efeito colateral (registro de models, `load_dotenv`).

---

## 20. Logging por print e configuração fixa → Logger e módulo de config

**Quanto aplicar:** Quando houver `print`/`console.log` nas camadas, ou porta, host e URI de banco escritos como literal.

**Antes:**

```python
print("Criando pedido", pedido_id)
app.run(host="0.0.0.0", port=5000)
```

**Depois:**

```python
# config/settings.py
PORT = int(os.environ.get("PORT", "5000"))
HOST = os.environ.get("HOST", "127.0.0.1")

logger = logging.getLogger(__name__)
logger.info("Criando pedido %s", pedido_id)
app.run(host=HOST, port=PORT)
```

**Transformação:**

- `print` trocado por `logger.info`
- Porta e host lidos de variáveis de ambiente
- Defaults seguros definidos em `config/settings.py`

**Pontos de atenção:**

- Os valores padrão devem ser seguros: debug desligado, host `127.0.0.1`.
- Nunca registre dados sensíveis no log (seção 3) e liste as novas variáveis no `.env.example`.

---

## Priorização recomendada

Aplique as seções nesta ordem e valide a aplicação a cada etapa. Os números seguem as seções acima.

### Crítico (segurança)

1. **2** Credenciais hardcoded
2. **1** SQL Injection
3. **4** Armazenamento inseguro de senha
4. **3** Exposição de dados sensíveis
5. **5** Endpoints admin ou debug expostos

### Alto impacto (arquitetura)

1. **6** God Class / God Module
2. **8** Estado global mutável
3. **10** Acoplamento forte
4. **7** Regra de negócio no Controller/Model
5. **9** Ausência de autenticação/autorização (depois que as camadas existirem)

### Robustez

1. **13** Validação de entrada
2. **14** Tratamento de erro genérico
3. **15** Operação multi-passo sem transação
4. **16** Callback hell

### Melhoria contínua

1. **11** Query N+1
2. **12** Código duplicado
3. **17** APIs deprecated
4. **18** Magic numbers e strings
5. **19** Nomes ruins e código morto
6. **20** Logging por print e configuração fixa
