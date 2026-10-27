# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`, refatorada para MVC em camadas: `routes/ → controllers/ → services/ → repositories/ → models/`, com `views/` (serializers), `middlewares/` (erros e auth) e `config/` (settings e constantes).

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # preencha SECRET_KEY (obrigatório)
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5001`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.
