# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-08-26

### Added
- Integração do **Flask-Limiter** para controle de taxa (Rate Limiting) de requisições.
- Limites específicos nas rotas de autenticação (cadastro, login, recuperação de senha).
- Limites específicos nas rotas de quiz (upload de bancos e execução).
- Limites específicos nas rotas administrativas (`/admin/*`).
- Novo blueprint `/health` para monitoramento de integridade e prontidão da aplicação (`/health/`, `/health/live`, `/health/ready`).
- Verificação de conectividade com o banco de dados (compatível com SQLAlchemy 2.0) na rota `/health`.
- Token opcional de autenticação (`HEALTH_CHECK_TOKEN`) para proteger os diagnósticos detalhados do banco de dados.
- Suíte completa de testes automatizados (`tests/test_health.py` e `tests/test_limiter.py`) validando todas as regras e comportamento de rate limiting e health check.

### Changed
- Configurações do projeto estendidas com suporte a Redis no ambiente produtivo (`ProductionConfig`) para sincronização de rate limit entre workers do Gunicorn.
- Resolução de `ResourceWarning: unclosed database` nos testes automatizados, liberando conexões SQLite devidamente no `tearDown`.
- Bumping da versão da aplicação de `1.2.0` para `1.3.0`.

### Documentation
- Atualizado o [README.md](README.md) detalhando as novas regras de rate limit, endpoints de saúde e guia para integração com monitoramento externo via UptimeRobot.
