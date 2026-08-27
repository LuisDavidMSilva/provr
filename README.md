![Provr](app/static/img/provr_logo.svg)

A web-based test application platform. Create accounts, upload question banks, take timed quizzes by difficulty level, and track your performance history.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Issues](https://img.shields.io/github/issues/LuisDavidMSilva/provr)
![Closed Issues](https://img.shields.io/github/issues-closed/LuisDavidMSilva/provr)
![Last Commit](https://img.shields.io/github/last-commit/LuisDavidMSilva/provr)

## How to use

1. Create an account at [provr.luishomelab.tec.br](https://provr.luishomelab.tec.br)
2. Generate a question bank using any AI chatbot with the prompt below
3. Save as `.json` or `.txt` and upload in **My Banks**
4. Configure your quiz — quantity, level and time limit
5. Start and track your results in **My Results**

### Question bank prompt template
```
Generate a question bank about [TOPIC] with [N] questions in JSON format:
[
  {
    "text": "Question text",
    "level": "easy|medium|hard",
    "topic": "topic name",
    "alternatives": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A"
  }
]
Return ONLY the JSON array, no additional text.
```

## Live Demo

[provr.luishomelab.tec.br](https://provr.luishomelab.tec.br)


## Stack

- Python 3.14 + Flask 3.x
- Flask-SQLAlchemy + Flask-Migrate
- SQLite (dev) / PostgreSQL (prod)

## Running locally

1. Clone the repository
```bash
    git clone https://github.com/LuisDavidMSilva/provr.git
    cd provr/
```
2. Create and activate the virtual environment
```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
3. Install dependencies
```bash
   pip install -r requirements.txt
```
4. Create your `.env` based on `.env.example`

5. Generate a SECRET_KEY
```bash
   python -c "import secrets; print(secrets.token_hex(32))"
```
6. Run migrations
```bash
   flask --app run db upgrade
```
7. Start the server
```bash
   python run.py
```

### Running tests

To run the automated test suite, make sure your virtual environment is active and execute:
```bash
python -m unittest discover -s tests
```


## Project structure
```
provr/
├── app/
│   ├── blueprints/       # Routes organized by domain
│   ├── models/           # Database models
│   ├── static/
│   └── templates/
├── docs/
│   ├── use-cases.md
│   └── data-modeling.md
├── migrations/
├── config.py
├── run.py
└── .env.example
```

## Documentation

- [Use cases](docs/use-cases.md)
- [Data modeling](docs/data-modeling.md)

## Rate Limiting & Health Check

### 🔒 Rate Limiting
A aplicação utiliza o **Flask-Limiter** para controlar e limitar abusos e ataques de força bruta. 

* **Limites Padrão:**
  * Global (padrão): `200 por dia` e `50 por hora`.
  * Rota `/auth/register`: `3 por hora` (proteção contra spam).
  * Rota `/auth/login`: `5 por minuto` (proteção contra brute-force).
  * Rotas `/auth/reset-password*`: `5 por hora`.
  * Rota `/quiz/upload`: `10 por minuto`.
  * Rota `/quiz/take`: `60 por minuto`.
  * Rotas Administrativas (`/admin/*`): `30 por minuto`.

* **Storage (Persistência):**
  * Em **desenvolvimento**, utiliza armazenamento em memória local (`memory://`).
  * Em **produção**, lê dinamicamente da variável de ambiente `REDIS_URL` para compartilhar os contadores entre múltiplos workers do Gunicorn.

* **Resposta de Erro:**
  * Requisições normais de navegadores (HTML) que excedem o limite são redirecionadas com uma mensagem de erro `flash`.
  * Requisições de API (JSON) recebem o status HTTP `429 Too Many Requests` com uma resposta estruturada:
    ```json
    {
      "error": "Too many requests",
      "message": "..."
    }
    ```

* **Headers HTTP Retornados:**
  * `X-RateLimit-Limit`: Quantidade limite de requisições.
  * `X-RateLimit-Remaining`: Requisições restantes na janela.
  * `X-RateLimit-Reset`: Timestamp UNIX quando a janela reinicia.

---

### 🏥 Health Check & Monitoramento
O blueprint de monitoramento está disponível sob o prefixo `/health/` e todas as suas rotas são isentas de rate limits (`@limiter.exempt`).

* **Endpoints:**
  * `GET /health/`: Diagnóstico completo. Verifica a conectividade do banco de dados (SQLAlchemy) e retorna metadados como versão, tempo de atividade (`uptime`) e ambiente.
  * `GET /health/live`: Liveness probe público (retorna `{ "alive": true }`).
  * `GET /health/ready`: Readiness probe público (retorna `{ "ready": true }`).

* **🔒 Autenticação do Health Check (Opcional):**
  * Para proteger o endpoint detalhado `/health/` em produção, configure a variável de ambiente `HEALTH_CHECK_TOKEN`.
  * Se configurada, o cliente deve enviar o cabeçalho `X-Health-Token` ou o parâmetro `?token=` com o valor correto para receber os dados de diagnóstico; caso contrário, receberá `401 Unauthorized`.

* **🚨 Configurando o UptimeRobot (VPS):**
  1. Acesse o painel do [UptimeRobot](https://uptimerobot.com/).
  2. Crie um novo monitor do tipo `HTTP(s)`.
  3. Insira a URL completa do endpoint: `https://seusite.com/health/` (ou envie o token de cabeçalho `X-Health-Token` caso esteja ativado).
  4. Defina o intervalo de verificação (ex: 5 minutos) e configure os alertas de e-mail/Telegram para o status HTTP != `200`.