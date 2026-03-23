FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.10.12 /uv /usr/local/bin/uv

WORKDIR /app

# Install deps
COPY pyproject.toml .
RUN uv pip install --system --no-cache -e .

# Copy source
COPY . .

# Non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
