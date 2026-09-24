FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL authors="DanilChagarnoy"

COPY . /app

ENV UV_NO_DEV=1

WORKDIR /app
RUN uv sync --locked

CMD ["sh", "-c", "uv run alembic upgrade head && uv run main"]