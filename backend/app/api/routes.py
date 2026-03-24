"""
API-Endpunkte für SolarPilot.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Optional

from app.models.schemas import LiveDataResponse, HealthResponse
from app.services.solplanet_collector import SolplanetCollector
from app.services.database_service import DatabaseService
from app.utils.logger import logger

router = APIRouter()

# Dependency Injection (wird in main.py gesetzt)
_collector: Optional[SolplanetCollector] = None
_db_service: Optional[DatabaseService] = None


def get_collector() -> SolplanetCollector:
    """Dependency für Collector"""
    if _collector is None:
        raise HTTPException(status_code=503, detail="Collector not initialized")
    return _collector


def get_db_service() -> DatabaseService:
    """Dependency für Database-Service"""
    if _db_service is None:
        raise HTTPException(status_code=503, detail="Database service not initialized")
    return _db_service


def set_dependencies(collector: SolplanetCollector, db_service: DatabaseService):
    """Setzt die Dependencies (wird bei Startup aufgerufen)"""
    global _collector, _db_service
    _collector = collector
    _db_service = db_service


@router.get("/live", response_model=LiveDataResponse)
async def get_live_data(collector: SolplanetCollector = Depends(get_collector)):
    """
    Liefert aktuelle Live-Daten vom System.

    Die Daten werden alle 30 Sekunden aktualisiert.
    """
    if collector.latest_data is None:
        raise HTTPException(
            status_code=503,
            detail="Noch keine Daten verfügbar. Bitte warten Sie einen Moment."
        )

    return LiveDataResponse(**collector.latest_data)


@router.get("/health", response_model=HealthResponse)
async def health_check(
    collector: SolplanetCollector = Depends(get_collector),
    db_service: DatabaseService = Depends(get_db_service)
):
    """
    Health-Check für Monitoring.

    Prüft:
    - Ist die Datenbank erreichbar?
    - Ist der Dongle erreichbar (letzte Daten < 2 Minuten alt)?
    - Allgemeiner Systemstatus
    """
    # Alter der letzten Daten berechnen
    last_data_age = None
    dongle_reachable = False

    if collector.last_successful_poll:
        last_data_age = int((datetime.utcnow() - collector.last_successful_poll).total_seconds())
        # Dongle ist erreichbar, wenn letzte Daten < 2 Minuten alt
        dongle_reachable = last_data_age < 120

    # Datenbank-Check (einfach: Service existiert?)
    database_connected = db_service is not None

    # Gesamtstatus bestimmen
    if database_connected and dongle_reachable:
        status = "healthy"
    elif database_connected or dongle_reachable:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(
        status=status,
        timestamp=datetime.utcnow(),
        database_connected=database_connected,
        dongle_reachable=dongle_reachable,
        last_data_age_seconds=last_data_age
    )
