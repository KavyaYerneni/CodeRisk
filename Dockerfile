# CPU-only CodeRisk API image. Mount model artifacts at /models.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CODERISK_MODEL_DIR=/models \
    CODERISK_LOG_LEVEL=INFO

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin coderisk

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY configs ./configs

RUN pip install --upgrade pip \
    && pip install . \
    && chown -R coderisk:coderisk /app

USER coderisk

EXPOSE 8742

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8742/health')"

CMD ["uvicorn", "coderisk.api.main:app", "--host", "0.0.0.0", "--port", "8742"]
