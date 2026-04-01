# Provr

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Issues](https://img.shields.io/github/issues/LuisDavidMSilva/provr)
![Closed Issues](https://img.shields.io/github/issues-closed/LuisDavidMSilva/provr)
![Last Commit](https://img.shields.io/github/last-commit/LuisDavidMSilva/provr)

## Live Demo

[provr.luishomelab.tec.br](https://provr.luishomelab.tec.br)

A web-based test application platform. Create accounts, upload question banks, take timed quizzes by difficulty level, and track your performance history.

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