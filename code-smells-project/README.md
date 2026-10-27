# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # defina SECRET_KEY
export $(grep -v '^#' .env | xargs)
python app.py
```

Rotas protegidas exigem `Authorization: Bearer <token>`; o token vem em `dados.token` do `POST /login`.

A aplicação sobe em `http://127.0.0.1:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.
