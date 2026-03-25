FROM python:3.14.2-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PYTHON_DOWNLOADS=0

# Set working directory
WORKDIR /app

# Copy workspace files for dependency resolution
COPY pyproject.toml uv.lock ./
COPY bot/pyproject.toml ./bot/

# Install bot dependencies (omit dev dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy the bot code
COPY bot/ ./bot/

# Run the bot
CMD ["uv", "run", "bot/bot.py"]
