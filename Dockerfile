FROM python:3.11-slim-bookworm@sha256:8be8e0e98a3eba91d8c0bdfd13a25e6ff7dac1e9d44708bfbeacc3a9b3c6f5f8

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /work

RUN apt-get update \
    && apt-get install -y --no-install-recommends git build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests

RUN pip install --upgrade pip \
    && pip install -e ".[dev]"

ENV LEDGERMEM_BASE_URL=https://api.proofly.dev

ENTRYPOINT ["ledgermem-eval"]
CMD ["run", "--benchmark", "longmemeval", "--mock", "--output", "/work/results"]
