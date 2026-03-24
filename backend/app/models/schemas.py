"""
Pydantic-Schemas für API-Request/Response-Modelle.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LiveDataResponse(BaseModel):
    """Response-Schema für /api/live Endpunkt"""

    timestamp: datetime

    # PV-Erzeugung
    pv_total_power: float = Field(..., description="Gesamt-PV-Leistung in kW")
    pv_east_power: float = Field(..., description="Ost-PV-Leistung in kW")
    pv_west_power: float = Field(..., description="West-PV-Leistung in kW")

    # Batterie
    battery_soc: float = Field(..., description="Ladestand in %", ge=0, le=100)
    battery_power: float = Field(..., description="Batterieleistung in kW (+ = Laden, - = Entladen)")
    battery_voltage: Optional[float] = Field(None, description="Batteriespannung in V")
    battery_current: Optional[float] = Field(None, description="Batteriestrom in A")
    battery_temperature: Optional[float] = Field(None, description="Batterietemperatur in °C")

    # Netz
    grid_power: float = Field(..., description="Netzleistung in kW (+ = Bezug, - = Einspeisung)")
    grid_frequency: Optional[float] = Field(None, description="Netzfrequenz in Hz")

    # Hausverbrauch
    house_consumption: float = Field(..., description="Hausverbrauch in kW", ge=0)

    # Status
    inverter_status: str = Field(..., description="Wechselrichter-Status")

    class Config:
        from_attributes = True  # Ermöglicht Konvertierung von SQLAlchemy-Modellen


class HealthResponse(BaseModel):
    """Response-Schema für /api/health Endpunkt"""

    status: str = Field(..., description="Gesundheitsstatus: healthy, degraded, unhealthy")
    timestamp: datetime = Field(..., description="Zeitstempel des Health-Checks")
    database_connected: bool = Field(..., description="Ist die Datenbank erreichbar?")
    dongle_reachable: bool = Field(..., description="Ist der Dongle erreichbar?")
    last_data_age_seconds: Optional[int] = Field(None, description="Alter der letzten Daten in Sekunden")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-03-24T10:30:00",
                "database_connected": True,
                "dongle_reachable": True,
                "last_data_age_seconds": 25
            }
        }
