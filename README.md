# API com Rate Limiting — Python + DDD + TDD + SOLID + Swagger

## Objetivo do projeto

Este projeto demonstra a construção de uma API em Python com arquitetura limpa
e boas práticas de engenharia de software, com foco em manutenibilidade,
testabilidade e escalabilidade.

Desenvolvi esta API de utilizadores (criar, listar, buscar e apagar) para
demonstrar como estruturo uma aplicação profissional: o pedido chega pelo HTTP,
transforma-se num caso de uso, atravessa a regra de negócio isolada no domínio
e regressa como resposta — com proteção de rate limiting, testes automatizados
e documentação interativa. Os conceitos aplicados:

- **DDD (Domain-Driven Design)** — separação entre regra de negócio e detalhes
  técnicos (HTTP, base de dados, frameworks), protegendo o núcleo do sistema.
- **SOLID** — classes coesas, com responsabilidade única e dependências
  explícitas, fáceis de testar e de substituir.
- **TDD (Test-Driven Development)** — testes escritos junto com o código,
  garantindo segurança para refatorar sem regressões.
- **Rate Limiting** — proteção contra abuso, limitando o número de requisições
  por cliente num intervalo de tempo, com resposta padronizada (HTTP 429).
- **Swagger (OpenAPI)** — documentação interativa gerada a partir do próprio
  código, permitindo explorar e testar a API no navegador.

> **Nota:** esta API limita o número de pedidos que cada cliente pode fazer
> num determinado período (60 requisições/minuto por IP, por defeito),
> respondendo com HTTP 429 e cabeçalho `Retry-After` quando o limite é excedido.

## Stack
- **Python + FastAPI** (Swagger em `/docs`, ReDoc em `/redoc`, OpenAPI em `/openapi.json`)
- **DDD** em 4 camadas: `domain` → `application` → `infrastructure` → `presentation`
- **Rate Limiting**: sliding window em memória por IP (60 req/min), cabeçalhos `X-RateLimit-*` + `Retry-After`, 429 padronizado
- **Persistência**: em memória por defeito; PostgreSQL via SQLAlchemy com `DATABASE_URL`
- **TDD**: `pytest` com testes unitários e de integração (`pytest -v`)
- **SOLID**: mapeado abaixo
- **Outros**: Pydantic v2, CORS, health check, paginação, injeção de dependência, Docker, `.env`

## Como executar
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# documentação: http://localhost:8000/docs
```

```bash
pytest -v
```

```bash
docker compose up --build
```

Com PostgreSQL (perfil `postgres`):
```bash
DATABASE_URL=postgresql+psycopg2://api:api@db:5432/api \
  docker compose --profile postgres up --build
```

## Estrutura
```
app/
  main.py                  # composição: app, middlewares, handlers e rotas
  core/                    # configuração (.env) e logging
  domain/                  # núcleo: entidades, value objects, interfaces e erros
  application/             # casos de uso e DTOs
  infrastructure/          # repositórios (memória/SQLAlchemy), rate limiter
  presentation/            # rotas HTTP, schemas, middlewares e handlers de erro
tests/
  unit/                    # Email, User, casos de uso, rate limiter
  integration/             # API por HTTP (inclui 429) e repositório SQL
```

## DDD
| Camada | Responsabilidade | Pode depender de |
|---|---|---|
| domain | regra de negócio pura, sem frameworks | apenas stdlib |
| application | orquestração dos casos de uso | domain |
| infrastructure | adaptadores concretos (memória, SQL, Redis) | domain, application |
| presentation | interface HTTP: rotas, validação, middlewares | application, domain, infrastructure |

Princípio central: dependências apontam sempre para dentro. O domínio
desconhece o FastAPI — e é exatamente assim que deve ser.

## SOLID (com exemplos do código)
- **S — Responsabilidade única** — `CreateUserUseCase` apenas cria utilizadores;
  `RateLimitMiddleware` apenas limita requisições; `Settings` apenas lê configuração.
- **O — Aberto/Fechado** — suportar Redis ou Postgres significa adicionar uma classe
  que implementa a interface existente; os casos de uso permanecem intactos.
- **L — Substituição de Liskov** — qualquer `IUserRepository` (memória ou SQL)
  pode ser injetado sem alterar o comportamento dos casos de uso.
- **I — Segregação de interfaces** — portas enxutas (`save/get/list/delete`),
  sem métodos desnecessários.
- **D — Inversão de dependência** — casos de uso e middlewares recebem abstrações
  via construtor/DI (`Depends`); nunca instanciam infraestrutura diretamente.

## Persistência
- Por defeito: **memória** (zero configuração; ideal para desenvolvimento e testes).
- Com `DATABASE_URL`: **PostgreSQL via SQLAlchemy** (`SQLAlchemyUserRepository`,
  mesma interface `IUserRepository` — nenhum caso de uso é alterado).
- O `docker-compose` inclui o serviço `db` (Postgres 16) no perfil `postgres`.

## Rate Limiting
- Algoritmo: **sliding window** de 60s por IP (regista o instante de cada pedido).
- Respeita `X-Forwarded-For` (cenários com proxy/reverse proxy).
- Rotas isentas: `/health`, `/docs`, `/redoc`, `/openapi.json`.
- Configuração por ambiente: `RATE_LIMIT_PER_MINUTE`, `RATE_LIMIT_ENABLED`.
- Evolução para Redis: implementar `RedisRateLimiter` com o mesmo método `is_allowed(key)`.
- Teste: `tests/integration/test_api.py::test_rate_limit_bloqueia_429`.

## Swagger
Gerado automaticamente a partir das rotas e schemas:
- `POST /api/v1/users` → 201 | 409 | 422 | 429
- `GET /api/v1/users?limit=&offset=` | `GET /api/v1/users/{id}` | `DELETE /api/v1/users/{id}`
- `GET /health`

## TDD
Ordem de construção: `Email` → `User` → `casos de uso` → `rate limiter` → `API`.
Cobertura opcional: `pip install pytest-cov && pytest --cov=app`.

## Licença
MIT — ver [LICENSE](LICENSE).
