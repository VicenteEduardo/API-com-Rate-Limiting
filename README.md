# API com Rate Limiting — Python + DDD + TDD + SOLID + Swagger

## Objetivo do projeto

Este projeto demonstra a construção de uma API em Python com arquitetura limpa
e boas práticas de engenharia de software, com foco em manutenibilidade,
testabilidade e escalabilidade.

A proposta é simples de propósito: uma API de utilizadores (criar, listar,
buscar e apagar) que serve de base para estudar e aplicar os conceitos que o
mercado mais valoriza:

- **DDD (Domain-Driven Design)** — separar a regra de negócio dos detalhes
  técnicos (HTTP, banco de dados, frameworks), protegendo o coração do sistema.
- **SOLID** — classes pequenas, cada uma com uma responsabilidade clara e
  dependências explícitas, fáceis de testar e de trocar quando for preciso.
- **TDD (Test-Driven Development)** — testes escritos junto com o código,
  garantindo segurança para refatorar sem medo de quebrar o que já funciona.
- **Rate Limiting** — proteção contra abuso, limitando o número de requisições
  por cliente num intervalo de tempo, com resposta padronizada (HTTP 429).
- **Swagger (OpenAPI)** — documentação viva e interativa, gerada a partir do
  próprio código, para qualquer pessoa explorar e testar a API no navegador.

Se dominares a estrutura deste projeto, dominas o esqueleto de praticamente
qualquer API profissional: o pedido chega pelo HTTP, transforma-se num caso
de uso, atravessa a regra de negócio e regressa como resposta.

> **Nota:** esta API limita o número de pedidos que cada cliente pode fazer
> num determinado período (60 requisições/minuto por IP, por defeito),
> respondendo com HTTP 429 e cabeçalho `Retry-After` quando o limite é excedido.

## Stack
- **Python + FastAPI** (Swagger automatico em `/docs`, ReDoc em `/redoc`, OpenAPI em `/openapi.json`)
- **DDD** em 4 camadas: `domain` → `application` → `infrastructure` → `presentation`
- **Rate Limiting**: sliding window em memoria por IP (60 req/min padrao), headers `X-RateLimit-*` + `Retry-After`, 429 padronizado
- **TDD**: `pytest` com testes unitarios + integracao (rode `pytest -v`)
- **SOLID**: mapeado abaixo
- **Outros**: Pydantic v2, CORS, health check, paginacao, injecao de dependencia, Docker, `.env`

## Como rodar
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# docs: http://localhost:8000/docs
```

```bash
pytest -v
```

```bash
docker compose up --build
```

## Estrutura
```
app/
  main.py                  # junta tudo: cria o app, registra rotas e middlewares
  core/                    # configuracoes (.env) e logging
  domain/                  # o coracao: entidades, value objects, interfaces e erros
  application/             # casos de uso (o que o sistema sabe fazer) + DTOs
  infrastructure/          # implementacoes concretas: banco em memoria, rate limiter
  presentation/            # a porta de entrada: rotas HTTP, validacoes e middlewares
tests/
  unit/                    # testa cada pedaco isolado (Email, User, casos de uso, limiter)
  integration/             # testa a API de verdade, por HTTP (inclui o 429)
```

## DDD (de forma simples)
| Camada | O que faz | Pode conhecer |
|---|---|---|
| domain | regra pura, sem framework | nada (so Python puro) |
| application | organiza o passo a passo de cada acao | domain |
| infrastructure | detalhes concretos (memoria; amanha pode ser SQL/Redis) | domain, application |
| presentation | conversa com o mundo la fora (HTTP) | application, domain, infrastructure |

A regra de ouro: quem esta dentro nunca conhece quem esta fora. O dominio nao sabe
que existe FastAPI — e e assim que deve ser.

## SOLID (com exemplos deste codigo)
- **S (uma responsabilidade por classe)** — `CreateUserUseCase` so cria usuario,
  `RateLimitMiddleware` so limita requisicoes, `Settings` so le configuracao.
- **O (aberto p/ extensao, fechado p/ mudanca)** — quer Redis ou Postgres? Crie uma
  classe nova que respeite a interface; os casos de uso continuam iguais.
- **L (qualquer implementacao serve)** — o caso de uso pede um `IUserRepository`;
  tanto faz se atras dele tem memoria ou SQL, ele funciona do mesmo jeito.
- **I (interfaces pequenas)** — a porta do repositorio so tem `save/get/list/delete`,
  nada de metodo gigante que ninguem usa.
- **D (dependa de abstracao)** — ninguem da `new` na infra la dentro; tudo chega
  pronto pelo construtor ou pelo `Depends` do FastAPI.

## Rate Limiting
- Algoritmo: **sliding window** de 60s por IP (guarda quando cada pedido chegou).
- Respeita `X-Forwarded-For` (quando tem proxy na frente).
- Rotas livres (nunca bloqueiam): `/health`, `/docs`, `/redoc`, `/openapi.json`.
- Configure por env: `RATE_LIMIT_PER_MINUTE`, `RATE_LIMIT_ENABLED`.
- Para prod com Redis: crie um `RedisRateLimiter` com o mesmo metodo `is_allowed(key)`.
- Teste: `tests/integration/test_api.py::test_rate_limit_bloqueia_429`.

## Swagger
O FastAPI gera sozinho a partir das rotas e schemas:
- `POST /api/v1/users` → 201 | 409 | 422 | 429
- `GET /api/v1/users?limit=&offset=` | `GET /api/v1/users/{id}` | `DELETE /api/v1/users/{id}`
- `GET /health`

## TDD
A ordem em que foi construido: `Email` → `User` → `casos de uso` → `rate limiter` → `API`.
Cada passo tem teste em `tests/`. Cobertura opcional:
`pip install pytest-cov && pytest --cov=app`.
