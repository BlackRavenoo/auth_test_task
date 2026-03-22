FROM python:3.13-slim

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

ENV environment=production
ENV UV_CACHE_DIR=/app/.uv-cache

CMD ["uv", "run", "uvicorn", "src.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]