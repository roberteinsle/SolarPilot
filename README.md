# SolarPilot

**Intelligente PV-Verbrauchssteuerung für Raspberry Pi 4**

SolarPilot ist eine deutschsprachige Standalone-Webapp, die Ihre PV-Anlage überwacht und Ihnen sagt, wann der beste Zeitpunkt ist, um energieintensive Geräte wie Waschmaschine, Trockner und Geschirrspüler zu starten. Die App kombiniert Echtzeit-Daten vom Solplanet-Wechselrichter mit einem Dual-Forecast-System und maximiert so Ihren Eigenverbrauch.

---

## 📋 Überblick

- **Version:** 1.0.0 (Phase 1 - Fundament)
- **Betreiber:** Robert Einsle
- **Standort:** Stormarn, Schleswig-Holstein
- **PV-Anlage:** 15,575 kWp (Trina Solar Vertex S+ TSM-NEG9RC.27, 445W × 35 Module)
  - **Ost:** 14 Module = 6,23 kWp (~40%)
  - **West:** 21 Module = 9,345 kWp (~60%)
- **System:** Solplanet ASW015K-TH Wechselrichter + Ai-HB G2 Batterie (7 Module)

---

## 🚀 Features (Phase 1)

✅ **Live-Datensammlung** alle 30 Sekunden vom Solplanet Ai-Dongle
✅ **Deutsches Dashboard** mit Energiefluss-Visualisierung
✅ **Ost/West-Split** für asymmetrische Dachausrichtung
✅ **Batterie-Monitoring** (SOC, Lade-/Entladeleistung)
✅ **Netz-Monitoring** (Bezug/Einspeisung)
✅ **Hausverbrauch** (automatisch berechnet)
✅ **Pushover-Integration** für iOS-Push-Benachrichtigungen
✅ **Docker-Stack** (Backend, Frontend, Nginx, SQLite)
✅ **Async-First Backend** mit FastAPI
✅ **Responsive UI** mit React + TailwindCSS

---

## 🛠️ Technologie-Stack

### Backend
- **FastAPI** (asynchrones Python-Framework)
- **SQLite** (mit SQLAlchemy async)
- **aiohttp** (async HTTP-Client für Dongle-Polling)
- **Pushover** (iOS Push-Benachrichtigungen)

### Frontend
- **React 18** + **Vite**
- **TailwindCSS** (Styling)
- **Axios** (API-Client)

### Infrastructure
- **Docker** + **Docker Compose**
- **Nginx** (Reverse Proxy)
- **Raspberry Pi 4** (8 GB RAM)
- **Portainer** (Docker-Management)

---

## 📦 Voraussetzungen

### Auf dem Laptop (Entwicklung)
- Git
- Docker Desktop
- Python 3.13+ (optional, falls lokal ohne Docker entwickelt wird)
- Node.js 20+ (optional, falls lokal ohne Docker entwickelt wird)

### Auf dem Raspberry Pi 4 (Produktion)
- Raspberry Pi OS (64-bit empfohlen)
- Docker + Docker Compose
- Portainer (optional, aber empfohlen)
- Netzwerkzugriff auf den Solplanet Ai-Dongle (192.168.10.113)

### API-Keys
- **Google Solar API Key** (für Dachgeometrie-Erkennung in Phase 2)
- **Pushover Account** (App Token + User Key)
  - Registrierung: https://pushover.net
  - Einmalige Zahlung (~5€), kein Abo

---

## 🔧 Installation

### 1. Repository klonen

#### Auf dem Laptop:
```bash
cd /path/to/projects
git clone https://github.com/roberteinsle/SolarPilot.git
cd SolarPilot
```

#### Auf dem Raspberry Pi:
```bash
cd /home/pi
git clone https://github.com/roberteinsle/SolarPilot.git
cd SolarPilot
```

---

### 2. Umgebungsvariablen konfigurieren

Erstellen Sie eine `.env`-Datei aus der Vorlage:

```bash
cp .env.example .env
nano .env  # oder vi, vim, etc.
```

**⚠️ WICHTIG:** Die `.env`-Datei enthält sensible Daten und wird **niemals** in Git committed!

#### Minimal-Konfiguration:

```bash
# Dongle (sollte bereits passen)
DONGLE_IP=192.168.10.113
DONGLE_PORT=8484
DONGLE_SN=UR015K6052540222

# MPPT-Zuordnung (⚠️ MUSS überprüft werden!)
# Welcher MPPT ist Ost, welcher West?
# Vorgehensweise:
# 1. Morgens (8-10 Uhr) schauen: Welcher MPPT hat die höchste Leistung? → Ost
# 2. Nachmittags (14-16 Uhr) schauen: Welcher MPPT dominiert? → West
MPPT_EAST=1
MPPT_WEST=2,3

# Pushover (ERFORDERLICH für Push-Benachrichtigungen)
PUSHOVER_APP_TOKEN=<Ihr App Token>
PUSHOVER_USER_KEY=<Ihr User Key>
```

---

### 3. Dongle-API testen (WICHTIG!)

**⚠️ VOR dem ersten Start:** Die JSON-Struktur des Dongles ist noch unbekannt. Testen Sie manuell:

```bash
curl "http://192.168.10.113:8484/getdevdata.cgi?device=2&sn=UR015K6052540222" | jq .  # Wechselrichter
curl "http://192.168.10.113:8484/getdevdata.cgi?device=3&sn=UR015K6052540222" | jq .  # Smartmeter
curl "http://192.168.10.113:8484/getdevdata.cgi?device=4&sn=UR015K6052540222" | jq .  # Batterie
```

Analysieren Sie die JSON-Struktur und passen Sie `backend/app/services/solplanet_collector.py` an:
- MPPT-Keys (wahrscheinlich `vpv1`, `ipv1`, `ppv1` oder ähnlich)
- Batterie-Keys (`soc`, `pb`, `vb`, etc.)
- Netz-Keys (`pac`, `fac`, etc.)

**Die Beispiel-Keys im Code sind Platzhalter!**

---

## 🐳 Docker-Befehle

### Entwicklung (Laptop)

```bash
# Dev-Container starten (mit Hot-Reload)
docker-compose -f docker-compose.dev.yml up --build

# Im Browser öffnen:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8080/docs
# - Backend Health: http://localhost:8080/api/health
```

### Produktion (Raspberry Pi)

```bash
# Container bauen und starten
docker-compose up -d --build

# Logs anzeigen
docker-compose logs -f

# Nur Backend-Logs
docker-compose logs -f backend

# Container-Status prüfen
docker ps

# Container stoppen
docker-compose down

# Container neu starten
docker-compose restart

# Alles neu bauen (nach Code-Änderungen)
docker-compose down
docker-compose up -d --build
```

### Health-Check

```bash
# Auf dem Pi (lokal)
curl http://localhost/api/health

# Von extern (im Netzwerk)
curl http://<pi-ip>/api/health
```

Erwartete Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-24T10:30:00",
  "database_connected": true,
  "dongle_reachable": true,
  "last_data_age_seconds": 25
}
```

---

## 📱 Dashboard

Nach dem Start ist das Dashboard erreichbar unter:

- **Lokal auf dem Pi:** http://localhost
- **Im Netzwerk:** http://<pi-ip> (z.B. http://192.168.10.xxx)

Das Dashboard zeigt:
- ☀️ **PV-Erzeugung** (gesamt + Ost/West-Split)
- 🔋 **Batterie** (SOC in %, Lade-/Entladeleistung)
- 🏠 **Hausverbrauch** (berechnet)
- ⚡ **Netz** (Bezug/Einspeisung)

Die Daten werden **automatisch alle 30 Sekunden** aktualisiert.

---

## 🔍 Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
docker-compose logs backend

# Häufige Fehler:
# - .env fehlt → cp .env.example .env
# - Pushover-Keys fehlen → In .env eintragen
# - Dongle nicht erreichbar → Netzwerk prüfen
```

### Frontend zeigt Fehler

```bash
# Logs prüfen
docker-compose logs frontend

# Häufige Fehler:
# - Backend nicht erreichbar → docker-compose logs backend
# - Port 3000 belegt → docker-compose down && docker-compose up -d
```

### Keine Daten im Dashboard

```bash
# Backend-Health prüfen
curl http://localhost/api/health

# Datenbank prüfen
docker exec -it solarpilot-app bash
sqlite3 /app/data/solarpilot.db
SELECT * FROM live_data ORDER BY timestamp DESC LIMIT 10;
.exit

# Häufige Ursachen:
# - Dongle nicht erreichbar (IP falsch, Netzwerk-Problem)
# - Parsing-Fehler (JSON-Keys stimmen nicht → solplanet_collector.py anpassen)
# - Polling-Fehler (Logs prüfen)
```

### Pushover-Benachrichtigungen kommen nicht an

```bash
# Logs prüfen
docker-compose logs backend | grep -i pushover

# Prüfen ob Credentials korrekt:
grep PUSHOVER .env

# Manuell testen (außerhalb des Containers):
curl -X POST https://api.pushover.net/1/messages.json \
  -d "token=<PUSHOVER_APP_TOKEN>" \
  -d "user=<PUSHOVER_USER_KEY>" \
  -d "message=Test von SolarPilot"
```

### MPPT-Zuordnung falsch

Symptom: Ost/West-Split zeigt vertauschte Werte (Ost stark nachmittags, West stark morgens).

**Lösung:**
1. `.env` öffnen
2. `MPPT_EAST` und `MPPT_WEST` vertauschen
3. Container neu starten: `docker-compose restart backend`

---

## 📊 Datenbank

SolarPilot speichert alle Daten in SQLite:
- **Pfad:** `./data/solarpilot.db`
- **Polling:** Alle 30 Sekunden ein neuer Eintrag
- **Größe:** ~100 KB pro Tag (bei 30-Sek-Intervall)
- **Cleanup:** Alte Daten (>90 Tage) werden automatisch gelöscht

### Datenbank manuell inspizieren

```bash
docker exec -it solarpilot-app bash
sqlite3 /app/data/solarpilot.db

# Letzte 10 Einträge anzeigen
SELECT timestamp, pv_total_power, battery_soc, grid_power, house_consumption
FROM live_data
ORDER BY timestamp DESC
LIMIT 10;

# Tagesertrag berechnen (Beispiel)
SELECT
  DATE(timestamp) as date,
  ROUND(MAX(pv_total_power), 2) as max_power_kw,
  COUNT(*) as measurements
FROM live_data
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 7;

.exit
```

---

## 🔄 Updates

### Code-Updates auf dem Pi

```bash
cd /home/pi/SolarPilot

# Neuesten Code pullen
git pull origin main

# Container neu bauen und starten
docker-compose down
docker-compose up -d --build

# Logs prüfen
docker-compose logs -f
```

### Nur Backend aktualisieren

```bash
docker-compose up -d --build backend
```

### Nur Frontend aktualisieren

```bash
docker-compose up -d --build frontend
```

---

## 🎯 Nächste Schritte (nach Phase 1)

Sobald Phase 1 stabil läuft:

1. **MPPT-Monitoring:** 1-2 Tage Daten sammeln, um Ost/West-Zuordnung zu validieren
2. **Dongle-Parsing verfeinern:** Alle verfügbaren Felder auslesen (Temperatur, Status-Codes, etc.)
3. **UI-Design verbessern:** Animationen, bessere Farben, Mobile-Optimierung
4. **Datenbank-Cleanup:** Job für alte Daten (>90 Tage)
5. **Phase 2 vorbereiten:** Open-Meteo + Google Solar API Integration (Dual-Forecast)

---

## 📝 Entwicklung

### Lokal ohne Docker entwickeln

#### Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# .env im Root-Verzeichnis erstellen
export $(cat ../.env | xargs)  # Linux/Mac
# Windows: Manuell in PowerShell setzen

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### Frontend:
```bash
cd frontend
npm install

# .env erstellen
echo "VITE_API_URL=http://localhost:8080/api" > .env.local

npm run dev
```

### Code-Stil

- **Backend:** PEP 8 (Python)
- **Frontend:** ESLint + Prettier (empfohlen, aber nicht erzwungen)
- **Commits:** Aussagekräftige Commit-Messages (z.B. "Fix: Dongle-Parsing für MPPT3")

---

## 🤝 Beitragen

Dies ist ein privates Projekt, aber Feedback und Ideen sind willkommen!

- **Issues:** https://github.com/roberteinsle/SolarPilot/issues
- **Kontakt:** robert@einsle.com

---

## 📄 Lizenz

Copyright © 2026 Robert Einsle. Alle Rechte vorbehalten.

---

## 🙏 Danksagung

- **Solplanet** für den stabilen Wechselrichter
- **Trina Solar** für die effizienten Module
- **Pushover** für die einfache Push-Notification-API
- **FastAPI, React, Docker** und alle Open-Source-Projekte, die dies möglich machen

---

**Happy Solar Harvesting! ☀️🔋**
