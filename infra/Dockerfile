##############################################
# STAGE 1 — Builder: install dependencies
##############################################
FROM python:3.14.0-slim AS builder

# Set up working directory
WORKDIR /build

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files from project root (we're in /infra)
COPY ../requirements.txt .

# Install dependencies into /usr/local (to copy later)
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


##############################################
# STAGE 2 — Final image: minimal runtime
##############################################
FROM python:3.14.0-slim AS runtime

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy only necessary project files
COPY ../app ./app
COPY ../main.py .
COPY ../observability ./observability

# Create a non-root user (good security practice)
RUN useradd -m appuser
USER appuser

# Expose for API or telemetry
EXPOSE 8000

# Default command
CMD ["python", "main.py"]
