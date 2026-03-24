"""
SQLAlchemy-Datenbankmodelle für SolarPilot.
Async-First mit aiosqlite.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class LiveData(Base):
    """
    Tabelle für Live-Daten (alle 30 Sekunden).
    Speichert vollständigen Systemzustand inkl. MPPT-Details.
    """
    __tablename__ = "live_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # PV-Erzeugung (kW)
    pv_total_power = Column(Float)  # Gesamt
    pv_east_power = Column(Float)   # Ost-Dachseite (berechnet aus MPPT)
    pv_west_power = Column(Float)   # West-Dachseite (berechnet aus MPPT)

    # MPPT-Details (jeweils Spannung V, Strom A, Leistung kW)
    mppt1_voltage = Column(Float)
    mppt1_current = Column(Float)
    mppt1_power = Column(Float)

    mppt2_voltage = Column(Float)
    mppt2_current = Column(Float)
    mppt2_power = Column(Float)

    mppt3_voltage = Column(Float)
    mppt3_current = Column(Float)
    mppt3_power = Column(Float)

    # Batterie
    battery_soc = Column(Float)          # Ladestand in %
    battery_power = Column(Float)        # Leistung in kW (positiv = Laden, negativ = Entladen)
    battery_voltage = Column(Float)      # Spannung in V
    battery_current = Column(Float)      # Strom in A
    battery_temperature = Column(Float)  # Temperatur in °C

    # Netz
    grid_power = Column(Float)           # Leistung in kW (positiv = Bezug, negativ = Einspeisung)
    grid_frequency = Column(Float)       # Netzfrequenz in Hz

    # Hausverbrauch (berechnet: PV + Batterie + Netz)
    house_consumption = Column(Float)    # kW

    # Status
    inverter_status = Column(String)

    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
    )


class DailySummary(Base):
    """
    Tabelle für Tagesstatistiken.
    Wird für Monatsberichte verwendet (später).
    """
    __tablename__ = "daily_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)

    # Tagesstatistik (kWh)
    pv_total_energy = Column(Float)      # Gesamt-PV-Ertrag
    pv_east_energy = Column(Float)       # Ost-Ertrag
    pv_west_energy = Column(Float)       # West-Ertrag

    battery_charged = Column(Float)      # Batterie geladen
    battery_discharged = Column(Float)   # Batterie entladen

    grid_import = Column(Float)          # Netz-Bezug
    grid_export = Column(Float)          # Netz-Einspeisung

    house_consumption_total = Column(Float)  # Hausverbrauch gesamt

    # Autarkie-Kennzahlen (%)
    self_sufficiency = Column(Float)     # Wie viel vom Verbrauch aus PV+Batterie
    self_consumption = Column(Float)     # Wie viel PV direkt verbraucht


async def init_db(database_url: str):
    """
    Initialisiert die Datenbank (erstellt Tabellen falls nicht vorhanden).

    Args:
        database_url: SQLite-Datenbank-URL (z.B. "sqlite+aiosqlite:///./data/solarpilot.db")

    Returns:
        AsyncSessionmaker für DB-Zugriff
    """
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    # Tabellen erstellen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Session-Factory erstellen
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
