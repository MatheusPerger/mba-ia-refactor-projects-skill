# Análise do projeto (Heurísticas)

Este arquivo contém heurísticas de como identificar as tecnologias usadas no projeto, e permite não depender de conhecimento prévio na stack.

**Como usar (Fase 1):** siga a ordem abaixo. Procure primeiro os arquivos de manifesto (rápidos de ler), depois confirme no código. Se os dois divergirem, o código vence o manifesto.

**Regra para versões (linguagem, framework, libs):** nunca invente nem deduza de memória. Use só o que estiver escrito no projeto. Se tiver dúvida, escreva `Não informada`.

Ignore sempre `venv/`, `.venv/`, `node_modules/`, `__pycache__/`, `.git/`, `dist/`, `build/`.

## Sumário

- [Detecção de linguagem](#detecção-de-linguagem)
- [Detecção de framework](#detecção-de-framework-web)
- [Detecção de storage / banco de dados](#detecção-de-storage--banco-de-dados)
- [Mapeamento de arquitetura](#mapeamento-de-arquitetura-atual)

---

## Detecção de linguagem

Olhe o arquivo de dependências na raiz e confirme pela extensão dos arquivos de código. A linguagem principal é a que tem mais arquivos.

| Arquivo na raiz | Extensão | Linguagem |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile` | `.py` | Python |
| `package.json` | `.js`, `.mjs`, `.ts` | JavaScript / TypeScript |
| `pom.xml`, `build.gradle` | `.java` | Java |
| `composer.json` | `.php` | PHP |
| `Gemfile` | `.rb` | Ruby |
| `go.mod` | `.go` | Go |

Versão da linguagem: só se estiver escrita em `.python-version`, `pyvenv.cfg`, `engines` do `package.json` ou `.nvmrc`. Senão, `Não informada`.

---

## Detecção de framework web

### Passo 1 — Dependências

Procure estes nomes no arquivo de dependências. Anote a versão e as libs extras (CORS, ORM, validação).

Onde ler a versão, em ordem:

1. Versão exata no manifesto: `flask==3.1.1`, `"express": "4.18.2"`.
2. Se for faixa (`^4.18.2`, `>=3.0`, `~=3.0`): use a versão instalada, de `package-lock.json` ou `venv/lib/*/site-packages/<pacote>-<versão>.dist-info`.
3. Se não achar nenhuma: `Não informada`.

| Linguagem | Procure por | Framework |
|---|---|---|
| Python | `flask` / `django` / `fastapi` | Flask / Django / FastAPI |
| Node.js | `express` / `@nestjs/core` / `fastify` | Express / NestJS / Fastify |
| Java | `spring-boot-starter-web` | Spring Boot |
| PHP | `laravel/framework` | Laravel |
| Ruby | `rails` | Rails |

### Passo 2 — Confirme no código

| Sinal no código | Framework |
|---|---|
| `Flask(__name__)`, `Blueprint(...)` | Flask |
| `urls.py` + `settings.py` | Django |
| `FastAPI()`, `@app.get(...)` | FastAPI |
| `require('express')` + `express()`, `express.Router()` | Express |
| `@Controller()`, `@Module()` | NestJS |
| `@SpringBootApplication`, `@RestController` | Spring Boot |
| `Route::get(...)` em `routes/*.php` | Laravel |
| `ApplicationController`, `config/routes.rb` | Rails |

### Passo 3 — Entry point

Arquivo que sobe o servidor:

- Python: `app.run(...)`, `if __name__ == "__main__":`, `manage.py`
- Node: `app.listen(...)`, campo `main` ou script `start` do `package.json`
- Java: `SpringApplication.run(...)`
- PHP: `public/index.php`
- Ruby: `config.ru`

---

## Detecção de storage / banco de dados

### Passo 1 — Biblioteca e string de conexão

| Sinal | Banco |
|---|---|
| `sqlite3`, `better-sqlite3`, `sqlite:///x.db`, arquivos `.db` / `.sqlite` | SQLite |
| `:memory:` | SQLite em memória (dados somem ao reiniciar) |
| `psycopg2`, `asyncpg`, `pg`, `postgresql://` | PostgreSQL |
| `pymysql`, `mysql2`, `mysql://` | MySQL |
| `pymongo`, `mongoose` | MongoDB |
| `redis` | Redis |

### Passo 2 — SQL puro ou ORM

| Sinal | Tipo |
|---|---|
| `cursor.execute("SELECT ...")`, `db.run(...)`, `db.all(...)` | SQL puro |
| `db.Model`, `SQLAlchemy(`, `Model.query`, `sequelize`, `prisma` | ORM |

### Passo 3 — Tabelas

Procure `CREATE TABLE`, `__tablename__`, classes herdando de `db.Model` e pastas `migrations/`. Se não houver banco, escreva "nenhum".

---

## Mapeamento de arquitetura atual

### Passo 1 — Liste os arquivos

Para cada arquivo de código: caminho e número de linhas.

### Passo 2 — Descubra o papel de cada arquivo

Um arquivo com mais de um papel indica mistura de camadas.

| Papel | Como reconhecer |
|---|---|
| Rotas / View | `@app.route`, `@bp.route`, `router.get(...)` |
| Controller | Recebe `request`, valida a entrada, chama o model e devolve a resposta |
| Model | Faz `SELECT/INSERT/UPDATE/DELETE` ou herda de `db.Model` |
| Regra de negócio | Cálculos e `if` sobre preço, desconto, estoque, status |
| Config | `os.environ`, chaves, portas, `DEBUG` |
| Infra | Abre a conexão, cria tabelas, faz seed |

### Passo 3 — Defina o nível de organização

| O que existe | Nível |
|---|---|
| Poucos arquivos na raiz, sem pastas de código | Monolito sem camadas |
| Pastas `models/`, `routes/`, `services/`, `utils/` | Parcialmente em camadas |
| `controllers/`, `models/`, `views/` ou `routes/`, `config/` | Já em MVC |
| Uma classe única (`AppManager`, `Manager`) que faz tudo | God Class |

Pastas não garantem separação real. Abra os arquivos e confira se há SQL ou regra de negócio dentro das rotas.
