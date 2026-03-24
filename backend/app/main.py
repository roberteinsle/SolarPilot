"""
FastAPI Hauptanwendung für SolarPilot Backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime

from app.config import settings
from app.models.database import init_db
from app.services.solplanet_collector import SolplanetCollector
from app.services.database_service import DatabaseService
from app.services.pushover_service import PushoverService
from app.api import routes
from app.utils.logger import setup_logging, logger

# Globale Services
collector: SolplanetCollector = None
db_service: DatabaseService = None
pushover_service: PushoverService = None
collector_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle-Management für FastAPI.
    Startet und stoppt alle Services.
    """
    global collector, db_service, pushover_service, collector_task

    # ========================================
    # STARTUP
    # ========================================

    # Logging einrichten
    setup_logging()
    logger.info("=" * 70)
    logger.info("🚀 SolarPilot Backend startet...")
    logger.info(f"📍 Standort: Stormarn, Schleswig-Holstein")
    logger.info(f"⚡ PV-Anlage: {settings.pv_total_kwp} kWp (Ost: {settings.pv_east_kwp} kWp, West: {settings.pv_west_kwp} kWp)")
    logger.info(f"📡 Dongle: {settings.dongle_base_url}")
    logger.info(f"🔄 Polling-Intervall: {settings.poll_interval}s")
    logger.info("=" * 70)

    # Datenbank initialisieren
    database_url = f"sqlite+aiosqlite:///{settings.database_path}"
    session_factory = await init_db(database_url)
    db_service = DatabaseService(session_factory)
    logger.info(f"✅ Datenbank initialisiert: {settings.database_path}")

    # Collector initialisieren
    collector = SolplanetCollector()
    await collector.start()

    # Pushover initialisieren
    pushover_service = PushoverService()
    if pushover_service.enabled:
        logger.info("✅ Pushover konfiguriert")
    else:
        logger.warning("⚠️ Pushover nicht konfiguriert (PUSHOVER_APP_TOKEN oder PUSHOVER_USER_KEY fehlt)")

    # Dependencies für API-Routes setzen
    routes.set_dependencies(collector, db_service)

    # Collector-Task starten
    collector_task = asyncio.create_task(collector.collect_and_store(db_service))
    logger.info("✅ Collector-Task gestartet")

    # Startup-Benachrichtigung senden
    if pushover_service.enabled:
        await pushover_service.send_notification(
            message=f"SolarPilot wurde erfolgreich gestartet und sammelt jetzt Daten.\n\n"
                    f"🔋 PV-Anlage: {settings.pv_total_kwp} kWp\n"
                    f"📡 Polling: alle {settings.poll_interval}s",
            title="✅ SolarPilot gestartet"
        )

    logger.info("=" * 70)
    logger.info("✅ Alle Services gestartet - SolarPilot ist bereit!")
    logger.info("=" * 70)

    yield

    # ========================================
    # SHUTDOWN
    # ========================================

    logger.info("=" * 70)
    logger.info("🛑 SolarPilot wird heruntergefahren...")

    # Collector-Task stoppen
    if collector_task:
        collector_task.cancel()
        try:
            await collector_task
        except asyncio.CancelledError:
            pass

    # Collector stoppen
    if collector:
        await collector.stop()

    logger.info("✅ Shutdown abgeschlossen")
    logger.info("=" * 70)


# FastAPI-App erstellen
app = FastAPI(
    title="SolarPilot API",
    description="Backend für intelligente PV-Verbrauchssteuerung",
    version="1.0.0",
    lifespan=lifespan
)

# CORS-Middleware (für Entwicklung alle Origins erlauben)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion auf Frontend-URL einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-Router einbinden
app.include_router(routes.router, prefix="/api", tags=["SolarPilot"])


@app.get("/")
async def root():
    """Root-Endpoint"""
    return {
        "service": "SolarPilot Backend",
        "version": "1.0.0",
        "description": "Intelligente PV-Verbrauchssteuerung",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs"
    }
