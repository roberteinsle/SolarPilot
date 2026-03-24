"""
Logging-Konfiguration für SolarPilot.
"""

import logging
import sys
from app.config import settings


def setup_logging():
    """Konfiguriert das Logging-System"""

    # Log-Level aus Config
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Root-Logger konfigurieren
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Externe Libraries auf WARNING setzen
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


# Logger für die Anwendung
logger = logging.getLogger("solarpilot")
