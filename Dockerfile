# ==========================================
# TrueSight AI - Multi-stage Production Build
# ==========================================

# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI backend + FFmpeg runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (ffmpeg and ffprobe for video forensics, libglib for OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend application source
COPY backend/ ./backend/

# Copy compiled frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose default port (Render, Railway, Hugging Face, Fly.io, Cloud Run inject $PORT)
ENV PORT=8000
EXPOSE 8000

WORKDIR /app/backend

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
