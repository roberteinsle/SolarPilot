"""
Service für Datenbankoperationen.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.database import LiveData, DailySummary
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.utils.logger import logger


class DatabaseService:
    """Service für asynchrone Datenbankoperationen"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save_live_data(self, data: Dict[str, Any]):
        """
        Speichert Live-Daten in der Datenbank.

        Args:
            data: Dictionary mit Live-Daten
        """
        async with self.session_factory() as session:
            live_data = LiveData(
                timestamp=data["timestamp"],
                pv_total_power=data["pv_total_power"],
                pv_east_power=data["pv_east_power"],
                pv_west_power=data["pv_west_power"],
                mppt1_power=data.get("mppt1_power"),
                mppt1_voltage=data.get("mppt1_voltage"),
                mppt1_current=data.get("mppt1_current"),
                mppt2_power=data.get("mppt2_power"),
                mppt2_voltage=data.get("mppt2_voltage"),
                mppt2_current=data.get("mppt2_current"),
                mppt3_power=data.get("mppt3_power"),
                mppt3_voltage=data.get("mppt3_voltage"),
                mppt3_current=data.get("mppt3_current"),
                battery_soc=data["battery_soc"],
                battery_power=data["battery_power"],
                battery_voltage=data.get("battery_voltage"),
                battery_current=data.get("battery_current"),
                battery_temperature=data.get("battery_temperature"),
                grid_power=data["grid_power"],
                grid_frequency=data.get("grid_frequency"),
                house_consumption=data["house_consumption"],
                inverter_status=data["inverter_status"],
            )

            session.add(live_data)
            await session.commit()
            logger.debug(f"Live-Daten gespeichert: {data['timestamp']}")

    async def get_latest_data(self) -> Optional[LiveData]:
        """
        Holt die neuesten Live-Daten aus der Datenbank.

        Returns:
            LiveData-Objekt oder None
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(LiveData).order_by(desc(LiveData.timestamp)).limit(1)
            )
            return result.scalars().first()

    async def cleanup_old_data(self, days: int = 90):
        """
        Löscht alte Daten (älter als X Tage).

        Args:
            days: Anzahl Tage, die aufbewahrt werden sollen
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        async with self.session_factory() as session:
            result = await session.execute(
                select(LiveData).where(LiveData.timestamp < cutoff_date)
            )
            old_records = result.scalars().all()

            if old_records:
                for record in old_records:
                    await session.delete(record)

                await session.commit()
                logger.info(f"Alte Daten gelöscht: {len(old_records)} Einträge (älter als {days} Tage)")
            else:
                logger.debug(f"Keine alten Daten zum Löschen gefunden (> {days} Tage)")
