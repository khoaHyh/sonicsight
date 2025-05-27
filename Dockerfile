FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

COPY requirements.txt ./

RUN uv pip install --system --no-cache --requirement requirements.txt

COPY . .
RUN chown -R app:app /app

USER app

EXPOSE 5000

# Start the application
CMD ["python", "main.py"]
