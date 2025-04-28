FROM python:3.11.9-slim AS base

# ---

FROM base AS poetry
RUN pip install poetry-plugin-export

# ---

FROM poetry AS requirements-builder
WORKDIR /deps
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry export --without-hashes --format=requirements.txt > requirements.txt

# ---

FROM base AS builder
RUN apt-get update && \
    apt-get install -y git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=requirements-builder /deps/requirements.txt /deps/requirements.txt

RUN pip install --no-cache-dir -r /deps/requirements.txt

# ---

FROM base AS release
WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY env /app/env/
COPY src /app/src/

ENV PYTHONPATH="${PYTHONPATH}:/app"

EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
