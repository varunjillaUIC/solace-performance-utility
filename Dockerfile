# ============================
# Stage 1 - Build React UI
# ============================

FROM node:18-alpine AS frontend-builder

WORKDIR /app/ui

COPY src/solengineer/ui/package*.json ./

RUN npm install

COPY src/solengineer/ui/ ./

RUN npm run build

# ============================
# Stage 2 - Python Backend
# ============================

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

COPY --from=frontend-builder /app/ui/build ./src/solengineer/ui/build

EXPOSE 8000

WORKDIR /app/src

CMD ["python", "-m", "solengineer.launch"]