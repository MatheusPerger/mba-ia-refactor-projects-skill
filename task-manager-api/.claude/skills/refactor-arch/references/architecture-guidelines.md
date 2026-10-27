# Architecture Guidelines

## Objetivo
Define as diretrizes para a arquitetura MVC, ques será o alvo da Fase 3, mirando uma separação de responsabilidades que facilite as manutenções futuras. Tendo camadas de Models, Views/Routes e Controllers.

## Arquitetura MVC (Model-View-Controller)

MVC separa a aplicação em três camadas, cada uma com uma responsabilidade. Isso reduz o acoplamento e facilita manutenção e testes.

### Model (Modelo)
É a camada de dados e regras de negócio.

- Representa as entidades do domínio (Usuário, Pedido, Produto).
- Define a estrutura das entidades e seus invariantes (campos, tipos, relacionamentos).
- Pode conter comportamento simples da própria entidade (ex.: `pedido.calcular_total()`).
- Não conhece a View nem o Controller, nem HTTP.
- Não executa queries, não conhece HTTP e não formata resposta.

### View (Visão)
É a camada de apresentação.

- Renderiza os dados para o usuário (HTML, templates, JSON serializado).
- Não contém regra de negócio nem acessa o banco.
- Em APIs, costuma ser o formato da resposta (serializers, DTOs de saída).

### Controller (Controlador)
É a camada de orquestração, o intermediário entre as duas outras.

- Recebe a requisição (rota, parâmetros, body).
- Valida a entrada em nível de protocolo e chama o Model.
- Escolhe a View ou a resposta adequada e define o status HTTP.
- Deve ser fino: só coordena, sem lógica de negócio.

### Erros comuns (anti-patterns)
- Fat Controller: regra de negócio e queries SQL dentro do controller.
- Fat Model: o model faz de tudo, até formatação de resposta.
- Lógica na View: templates que consultam o banco ou decidem regras.
- God Class: um único arquivo com rotas, SQL e regras, comum em código legado.

## Camadas complementares

O MVC puro não define onde ficam a configuração, o roteamento, as regras de negócio, o acesso a dados e as preocupações transversais. Na refatoração, o MVC fica na borda (apresentação) e as camadas abaixo completam a arquitetura. O Model do MVC passa a ser composto por **Services** (regras), **Repositories** (dados) e **Models** (entidades).

### Config (Configuração)
Centraliza tudo que varia entre ambientes.

- Lê variáveis de ambiente (porta, URL do banco, chaves secretas, flags de debug) em um único lugar.
- Expõe os valores para o resto da aplicação por um objeto ou módulo de settings.
- Não contém regra de negócio nem valores sensíveis hardcoded. Segredos vêm do ambiente (`.env` fora do versionamento).
- Resolve: credenciais hardcoded, configuração fixa.

### Routes (Rotas)
Mapeia a requisição para o controller que a trata.

- Declara método HTTP + caminho e liga cada um a uma função de controller.
- Agrupa rotas por recurso (`/produtos`, `/pedidos`, `/usuarios`).
- Aplica middlewares específicos da rota (autenticação, validação), quando existirem.
- Não contém lógica, nem acessa dados, nem monta resposta.

### Services (Serviços)
Camada de regras de negócio e casos de uso.

- Implementa a lógica do domínio: cálculos, validações de negócio, decisões de fluxo.
- Orquestra um ou mais repositories e, quando há operação multi-passo, controla a transação.
- Lança erros de domínio (`NotFound`, `Validation`, `Conflict`), nunca respostas HTTP.
- Não conhece `request`, `response`, status code nem framework web. Deve ser testável sem subir o servidor.
- Resolve: regra de negócio no controller/model, código duplicado, acoplamento forte.

### Repositories (Repositórios)
Camada de acesso a dados.

- Executa queries e comandos de persistência (CRUD, buscas, joins) e devolve entidades ou estruturas simples.
- É o único lugar com SQL/ORM. Usa sempre queries parametrizadas.
- Resolve consultas em lote para evitar N+1.
- Não contém regra de negócio nem decide status HTTP.
- Resolve: SQL injection, query N+1, SQL espalhado pelo código.

### Middlewares (e tratamento de erros)
Preocupações transversais que atravessam várias rotas.

- **Tratamento de erros:** um handler central converte erros de domínio em respostas HTTP padronizadas (404, 400, 409, 500) e evita vazar stack trace ou detalhes internos.
- **Autenticação/autorização:** valida credenciais e permissões antes de chegar ao controller.
- **Logging:** registra requisições e erros com um logger configurável, no lugar de `print`.
- **Outros:** CORS, rate limit, parsing e validação de entrada.
- Não contém regra de negócio do domínio.

### Entrypoint / Composition Root
Ponto de entrada que monta a aplicação.

- Carrega a config, cria a conexão, instancia repositories → services → controllers e registra rotas e middlewares.
- Sobe o servidor. É o único lugar onde as dependências são conectadas.
- Não contém regra de negócio nem rotas definidas inline.

## Fluxo de uma requisição

```
Requisição
  → Middlewares (auth, log, parsing)
  → Route
  → Controller        (extrai dados, chama o service)
  → Service           (regras de negócio, transação)
  → Repository        (queries) → Banco
  ← Entidade (Model)
  ← Service
  ← Controller        (escolhe status, usa a View)
  ← View/Serializer   (formata a saída)
Resposta
Erros em qualquer ponto → Middleware de erros → Resposta padronizada
```

## Regras de dependência

A dependência aponta sempre para baixo. Uma camada nunca importa uma de cima.

```
Routes → Controllers → Services → Repositories → Models
                          ↓
                       Config (usada por todas, não depende de nenhuma)
```

## Estrutura de diretórios alvo

Adapte nomes e extensões à convenção da stack detectada na Fase 1. A separação por responsabilidade é o que importa.

```
projeto/
├── config/          # settings e conexão com o banco
├── routes/          # mapeamento URL → controller
├── controllers/     # camada HTTP
├── services/        # regras de negócio
├── repositories/    # acesso a dados
├── models/          # entidades
├── views/           # serializers / formatação de saída (ou templates)
├── middlewares/     # erros, auth, logging
└── app / main       # entrypoint (composition root)
```
