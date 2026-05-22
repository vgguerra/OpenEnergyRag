# syntax=docker/dockerfile:1.7

# Builder: install dependencies into a self-contained venv with uv.
FROM python:3.12-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY run.py ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Runtime: non-root user (UID 1000) so it works on Hugging Face Spaces
# and any other host that drops privileges. libgomp1 is required by
# ONNXRuntime under fastembed.
FROM python:3.12-slim AS runtime

ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FASTEMBED_CACHE_DIR=/app/.fastembed_cache \
    HF_HOME=/app/.hf_cache

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 user

WORKDIR /app

COPY --from=builder --chown=user:user /app/.venv ./.venv
COPY --chown=user:user src ./src
COPY --chown=user:user run.py ./

RUN mkdir -p /app/.fastembed_cache /app/.hf_cache \
    && chown -R user:user /app

USER user

EXPOSE 8000

CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
