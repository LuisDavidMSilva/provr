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
The application uses **Flask-Limiter** to control and throttle abuse and brute-force attacks.

* **Default Limits:**
  * Global (default): `200 per day` and `50 per hour`.
  * `/auth/register` route: `3 per hour` (spam protection).
  * `/auth/login` route: `5 per minute` (brute-force protection).
  * `/auth/reset-password*` routes: `5 per hour`.
  * `/quiz/upload` route: `10 per minute`.
  * `/quiz/take` route: `60 per minute`.
  * Administrative routes (`/admin/*`): `60 per minute`.

* **Storage (Persistence):**
  * In **development**, it uses local in-memory storage (`memory://`).
  * In **production**, it dynamically reads from the `REDIS_URL` environment variable to share counters across multiple Gunicorn workers.

* **Error Response:**
  * Standard browser requests (HTML) exceeding the limit are redirected with a `flash` error message.
  * API requests (JSON) receive an HTTP `429 Too Many Requests` status with a structured response:
    ```json
    {
      "error": "Too many requests",
      "message": "..."
    }
    ```

* **Returned HTTP Headers:**
  * `X-RateLimit-Limit`: Maximum number of requests.
  * `X-RateLimit-Remaining`: Remaining requests in the current window.
  * `X-RateLimit-Reset`: UNIX timestamp when the window resets.

---

### 🏥 Health Check & Monitoring
The monitoring blueprint is available under the `/health/` prefix, and all of its routes are exempt from rate limits (`@limiter.exempt`).

* **Endpoints:**
  * `GET /health/`: Full diagnostics. Checks database connectivity (SQLAlchemy) and returns metadata such as version, uptime, and environment.
  * `GET /health/live`: Public liveness probe (returns `{ "alive": true }`).
  * `GET /health/ready`: Public readiness probe (returns `{ "ready": true }`).

* **🔒 Health Check Authentication (Optional):**
  * To protect the detailed diagnostic endpoint `/health/` in production, configure the `HEALTH_CHECK_TOKEN` environment variable.
  * If configured, the client must send the `X-Health-Token` header or `?token=` query parameter with the correct value to receive diagnostic data; otherwise, it returns `401 Unauthorized`.

* **🚨 Setting up UptimeRobot (VPS):**
  1. Access the [UptimeRobot](https://uptimerobot.com/) dashboard.
  2. Create a new monitor of type `HTTP(s)`.
  3. Enter the full URL of the endpoint: `https://yourdomain.com/health/` (or send the `X-Health-Token` header if enabled).
  4. Set the check interval (e.g. 5 minutes) and configure email/Telegram alerts for HTTP status != `200`.