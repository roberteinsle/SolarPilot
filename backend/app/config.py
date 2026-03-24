"""
Konfigurationsmanagement für SolarPilot Backend.
Lädt alle Einstellungen aus Umgebungsvariablen (.env).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Zentrale Konfiguration für SolarPilot"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Dongle-Konfiguration
    dongle_ip: str = "192.168.10.113"
    dongle_port: int = 8484
    dongle_sn: str = "UR015K6052540222"

    # MPPT-Zuordnung (kommasepariert, z.B. "1" oder "2,3")
    mppt_east: str = "1"
    mppt_west: str = "2,3"

    # Anlagenparameter (Trina Solar Vertex S+ TSM-NEG9RC.27, 445W pro Modul)
    pv_total_kwp: float = 15.575
    pv_east_kwp: float = 6.23   # 14 Module
    pv_west_kwp: float = 9.345  # 21 Module

    # Polling
    poll_interval: int = 30  # Sekunden

    # Datenbank
    database_path: str = "/app/data/solarpilot.db"

    # Pushover (iOS Push-Benachrichtigungen)
    pushover_app_token: str = ""
    pushover_user_key: str = ""

    # Logging
    log_level: str = "INFO"

    @property
    def dongle_base_url(self) -> str:
        """Basis-URL für Dongle-API"""
        return f"http://{self.dongle_ip}:{self.dongle_port}"

    @property
    def mppt_east_list(self) -> List[int]:
        """MPPT-Indizes für Ost-Dachseite als Liste"""
        return [int(x.strip()) for x in self.mppt_east.split(",") if x.strip()]

    @property
    def mppt_west_list(self) -> List[int]:
        """MPPT-Indizes für West-Dachseite als Liste"""
        return [int(x.strip()) for x in self.mppt_west.split(",") if x.strip()]

    @property
    def pushover_enabled(self) -> bool:
        """Prüft, ob Pushover-Credentials konfiguriert sind"""
        return bool(self.pushover_app_token and self.pushover_user_key)


# Global verfügbares Settings-Objekt
settings = Settings()
