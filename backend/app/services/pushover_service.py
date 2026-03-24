"""
Service für Pushover-Benachrichtigungen (iOS Push).
"""

import aiohttp
from app.config import settings
from app.utils.logger import logger
from typing import Optional


class PushoverService:
    """Service für Pushover-Push-Benachrichtigungen"""

    PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

    def __init__(self):
        self.app_token = settings.pushover_app_token
        self.user_key = settings.pushover_user_key
        self.enabled = settings.pushover_enabled

    async def send_notification(
        self,
        message: str,
        title: Optional[str] = "SolarPilot",
        priority: int = 0
    ) -> bool:
        """
        Sendet eine Pushover-Benachrichtigung.

        Args:
            message: Nachrichtentext
            title: Titel der Nachricht (optional)
            priority: Priorität (-2 bis 2, Standard: 0 = Normal)

        Returns:
            True bei Erfolg, False bei Fehler

        Prioritäten:
            -2: Lautlos (keine Benachrichtigung)
            -1: Leise (keine Vibration/Sound)
             0: Normal
             1: Hoch (umgeht Ruhezeiten)
             2: Notfall (erfordert Bestätigung)
        """
        if not self.enabled:
            logger.warning("Pushover nicht konfiguriert. Benachrichtigung wird übersprungen.")
            return False

        payload = {
            "token": self.app_token,
            "user": self.user_key,
            "message": message,
            "title": title,
            "priority": priority,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.PUSHOVER_API_URL, data=payload) as response:
                    if response.status == 200:
                        logger.info(f"✅ Pushover-Benachrichtigung gesendet: {title}")
                        return True
                    else:
                        response_text = await response.text()
                        logger.error(f"❌ Pushover-Fehler: HTTP {response.status} - {response_text}")
                        return False
        except Exception as e:
            logger.error(f"❌ Fehler beim Senden der Pushover-Benachrichtigung: {e}")
            return False
