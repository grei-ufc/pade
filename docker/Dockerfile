FROM python:3.12-slim

LABEL maintainer="Pade Development <lucassmelo@dee.ufc.br>"
LABEL description="Framework for multiagent systems development in Python. This dockerfile builds a PADE environment."

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:${PATH}"
ENV UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /uvx /bin/

WORKDIR /app
COPY . /app

RUN uv sync --frozen

EXPOSE 3000/tcp
EXPOSE 8000/tcp
EXPOSE 8001/tcp

CMD ["sleep", "infinity"]
