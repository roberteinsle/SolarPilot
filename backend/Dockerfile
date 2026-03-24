FROM python:3.13-slim

WORKDIR /app

# System-Dependencies für curl (Health-Checks)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code kopieren
COPY app/ ./app/

# SQLite-Datenbank-Verzeichnis erstellen
RUN mkdir -p /app/data

# Port exponieren
EXPOSE 8080

# Uvicorn starten
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
