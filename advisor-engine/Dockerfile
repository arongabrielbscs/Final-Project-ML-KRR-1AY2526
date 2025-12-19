# ==========================================
# STAGE 1: Build the Frontend (Node.js)
# ==========================================
FROM node:22-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package.json first (better caching)
COPY frontend/package*.json ./
RUN npm install

# Copy source code and build
COPY frontend/ .
RUN npm run build
# Result: /app/frontend/dist now contains your website


# ==========================================
# STAGE 2: Build the Backend (Python)
# ==========================================
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (needed for some ML libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Backend Code
COPY backend/ ./backend

# Copy the Built Frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the port (Render/Fly.io sets the PORT env var automatically)
ENV PORT=8000
EXPOSE 8000

# Run the app
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"]