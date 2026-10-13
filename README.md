# API com Rate Limiting — Python + DDD + TDD + SOLID + Swagger

## Objetivo do projeto

Este projeto existe para mostrar, na pratica, como construir uma API em Python
bem organizada desde o primeiro dia — sem virar uma "bola de neve" dificil de manter.

A ideia e simples: uma API de usuarios (criar, listar, buscar, apagar) que serve
de exemplo para estudar e aplicar conceitos que o mercado cobra:

- **DDD**: separar o que e regra de negocio do que e detalhe tecnico (HTTP, banco, etc.).
- **SOLID**: deixar cada classe com uma responsabilidade clara e facil de trocar depois.
- **TDD**: escrever o teste antes (ou junto) do codigo, para ter seguranca ao mudar.
- **Rate Limiting**: proteger a API contra abuso, limitando quantas requisicoes cada IP pode fazer.
- **Swagger**: documentar a API de forma automatica, para qualquer pessoa testar no navegador.

Se voce entende este projeto, entende o esqueleto de quase qualquer API profissional:
entra pedido pelo HTTP, vira caso de uso, mexe no dominio e volta como resposta.

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
