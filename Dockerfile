# Stage 1: Build the frontend
FROM node:22-slim AS frontend
WORKDIR /app/ui
COPY ui/package.json ui/package-lock.json* ./
RUN npm ci
COPY ui/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

# Copy the built frontend
COPY --from=frontend /app/ui/dist ./ui/dist

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Run the server
CMD ["python", "-m", "uvicorn", "opengravity.server.app:app", "--host", "0.0.0.0", "--port", "8080"]
