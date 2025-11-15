# Multi-stage build: Node.js for frontend, Python for backend

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
# Also copy shared assets used by the frontend build
COPY assets/ /app/assets/
RUN npm run build

# Stage 2: Python backend with frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY models/ ./models/
COPY assets/ ./assets/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/web/dist ./web/dist

# Expose port
EXPOSE 8080

# Set environment variables
ENV API_HOST=0.0.0.0
ENV API_PORT=8080

# Run the application
CMD ["python", "api/main.py"]
