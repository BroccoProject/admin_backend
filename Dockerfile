FROM python:3.12-slim

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency definition
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv venv && uv sync --no-dev

# Copy application files
COPY . .

# Expose port
EXPOSE 8000

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Start server
CMD ["python", "src/main.py"]
