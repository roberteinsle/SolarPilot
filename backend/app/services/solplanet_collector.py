"""
Solplanet-Collector: Pollt den Ai-Dongle und sammelt Live-Daten.

⚠️ WICHTIG: Die JSON-Parsing-Logik muss noch angepasst werden!
Die echte API-Struktur ist noch unbekannt. Vor dem ersten Start:
1. Manuell alle 3 Endpunkte mit curl abrufen
2. JSON-Struktur analysieren
3. parse_live_data() anpassen (siehe Kommentare)
"""

import asyncio
import aiohttp
from datetime import datetime
from app.config import settings
from app.utils.logger import logger
from typing import Dict, Any, Optional


class SolplanetCollector:
    """
    Collector für Solplanet Ai-Dongle.
    Pollt alle 30 Sekunden die 3 API-Endpunkte parallel.
    """

    def __init__(self):
        self.base_url = settings.dongle_base_url
        self.serial_number = settings.dongle_sn
        self.session: Optional[aiohttp.ClientSession] = None
        self.latest_data: Optional[Dict[str, Any]] = None
        self.last_successful_poll: Optional[datetime] = None
        self._running = False

    async def start(self):
        """Startet den Collector mit eigener aiohttp-Session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        self._running = True
        logger.info("🚀 SolarplanetCollector gestartet")

    async def stop(self):
        """Stoppt den Collector und schließt die Session"""
        self._running = False
        if self.session:
            await self.session.close()
        logger.info("🛑 SolplanetCollector gestoppt")

    async def fetch_device_data(self, device_id: int) -> Optional[Dict[str, Any]]:
        """
        Holt Daten von einem Dongle-Endpunkt.

        Args:
            device_id: Device-ID (2=Wechselrichter, 3=Smartmeter, 4=Batterie)

        Returns:
            JSON-Response als Dictionary oder None bei Fehler
        """
        url = f"{self.base_url}/getdevdata.cgi?device={device_id}&sn={self.serial_number}"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"✅ Device {device_id} abgerufen: {len(str(data))} Bytes")
                    return data
                else:
                    logger.error(f"❌ Dongle-Anfrage fehlgeschlagen (Device {device_id}): HTTP {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Timeout beim Abrufen von Device {device_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen von Device {device_id}: {e}")
            return None

    async def poll_all_devices(self) -> Dict[str, Any]:
        """
        Pollt alle 3 Dongle-Endpunkte parallel.

        Returns:
            Dictionary mit Rohdaten von allen Geräten + Timestamp
        """
        tasks = [
            self.fetch_device_data(2),  # Wechselrichter
            self.fetch_device_data(3),  # Smartmeter
            self.fetch_device_data(4),  # Batterie
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "inverter": results[0] if not isinstance(results[0], Exception) else None,
            "smartmeter": results[1] if not isinstance(results[1], Exception) else None,
            "battery": results[2] if not isinstance(results[2], Exception) else None,
            "timestamp": datetime.utcnow()
        }

    def parse_live_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parst Rohdaten vom Dongle in strukturierte Form.

        ⚠️ TODO: Diese Methode muss angepasst werden!
        Die Keys im JSON sind noch unbekannt. Vorher mit curl testen:

        curl "http://192.168.10.113:8484/getdevdata.cgi?device=2&sn=UR015K6052540222"
        curl "http://192.168.10.113:8484/getdevdata.cgi?device=3&sn=UR015K6052540222"
        curl "http://192.168.10.113:8484/getdevdata.cgi?device=4&sn=UR015K6052540222"

        Dann die echten Keys hier eintragen!

        Args:
            raw_data: Rohdaten von poll_all_devices()

        Returns:
            Strukturiertes Dictionary für Datenbank
        """
        inverter = raw_data.get("inverter", {})
        battery = raw_data.get("battery", {})
        smartmeter = raw_data.get("smartmeter", {})

        # ⚠️ PLACEHOLDER: Diese Keys müssen angepasst werden!
        # Mögliche Key-Namen (unbestätigt):
        # - MPPT: vpv1/ipv1/ppv1, vpv2/ipv2/ppv2, vpv3/ipv3/ppv3
        # - Oder: mppt1_voltage, mppt1_current, mppt1_power
        # - Oder: pv1_voltage, pv1_current, pv1_power

        # MPPT-Leistungen extrahieren (W → kW)
        # TODO: Echte Keys verwenden!
        mppt1_power_w = inverter.get("ppv1", 0)  # ⚠️ Beispiel-Key
        mppt2_power_w = inverter.get("ppv2", 0)  # ⚠️ Beispiel-Key
        mppt3_power_w = inverter.get("ppv3", 0)  # ⚠️ Beispiel-Key

        mppt1_power = mppt1_power_w / 1000
        mppt2_power = mppt2_power_w / 1000
        mppt3_power = mppt3_power_w / 1000

        # Ost/West-Split berechnen basierend auf Config
        pv_east_power = sum([
            mppt1_power if 1 in settings.mppt_east_list else 0,
            mppt2_power if 2 in settings.mppt_east_list else 0,
            mppt3_power if 3 in settings.mppt_east_list else 0
        ])

        pv_west_power = sum([
            mppt1_power if 1 in settings.mppt_west_list else 0,
            mppt2_power if 2 in settings.mppt_west_list else 0,
            mppt3_power if 3 in settings.mppt_west_list else 0
        ])

        # Batterie-Daten
        # TODO: Echte Keys verwenden!
        battery_soc = battery.get("soc", 0)                # ⚠️ Beispiel-Key
        battery_power_w = battery.get("pb", 0)             # ⚠️ Beispiel-Key (pb = battery power?)
        battery_voltage = battery.get("vb", 0)             # ⚠️ Beispiel-Key
        battery_current = battery.get("ib", 0)             # ⚠️ Beispiel-Key
        battery_temp = battery.get("temp", 0)              # ⚠️ Beispiel-Key

        # Netz-Daten
        # TODO: Echte Keys verwenden!
        grid_power_w = smartmeter.get("pac", 0)            # ⚠️ Beispiel-Key
        grid_frequency = smartmeter.get("fac", 50)         # ⚠️ Beispiel-Key

        # Strukturierte Daten
        parsed = {
            "timestamp": raw_data["timestamp"],

            # PV (kW)
            "pv_total_power": mppt1_power + mppt2_power + mppt3_power,
            "pv_east_power": pv_east_power,
            "pv_west_power": pv_west_power,

            # MPPT-Details
            "mppt1_power": mppt1_power,
            "mppt1_voltage": inverter.get("vpv1", 0),      # ⚠️ Beispiel-Key
            "mppt1_current": inverter.get("ipv1", 0),      # ⚠️ Beispiel-Key

            "mppt2_power": mppt2_power,
            "mppt2_voltage": inverter.get("vpv2", 0),      # ⚠️ Beispiel-Key
            "mppt2_current": inverter.get("ipv2", 0),      # ⚠️ Beispiel-Key

            "mppt3_power": mppt3_power,
            "mppt3_voltage": inverter.get("vpv3", 0),      # ⚠️ Beispiel-Key
            "mppt3_current": inverter.get("ipv3", 0),      # ⚠️ Beispiel-Key

            # Batterie
            "battery_soc": battery_soc,
            "battery_power": battery_power_w / 1000,       # W → kW
            "battery_voltage": battery_voltage,
            "battery_current": battery_current,
            "battery_temperature": battery_temp,

            # Netz
            "grid_power": grid_power_w / 1000,             # W → kW
            "grid_frequency": grid_frequency,

            # Status
            "inverter_status": inverter.get("status", "unknown"),  # ⚠️ Beispiel-Key
        }

        # Hausverbrauch berechnen (Energiebilanz)
        # Formel: Hausverbrauch = PV + Batterie + Netz
        # Vorzeichen:
        #   - Batterie: positiv = Laden (Energie REIN), negativ = Entladen (Energie RAUS)
        #   - Netz: positiv = Bezug (Energie REIN), negativ = Einspeisung (Energie RAUS)
        #
        # ⚠️ WICHTIG: Falls die Formel nicht stimmt, Vorzeichen prüfen!
        parsed["house_consumption"] = max(0, (
            parsed["pv_total_power"] +
            parsed["battery_power"] +
            parsed["grid_power"]
        ))

        return parsed

    async def collect_and_store(self, db_service):
        """
        Hauptschleife: Daten sammeln und in DB speichern.
        Läuft kontinuierlich im Hintergrund.

        Args:
            db_service: DatabaseService-Instanz
        """
        logger.info(f"📡 Collector-Loop gestartet (Intervall: {settings.poll_interval}s)")

        while self._running:
            try:
                # Daten vom Dongle holen
                raw_data = await self.poll_all_devices()

                # Prüfen ob Daten vollständig
                if all([raw_data["inverter"], raw_data["battery"], raw_data["smartmeter"]]):
                    # Parsen
                    parsed_data = self.parse_live_data(raw_data)
                    self.latest_data = parsed_data
                    self.last_successful_poll = datetime.utcnow()

                    # In Datenbank speichern
                    await db_service.save_live_data(parsed_data)

                    logger.info(
                        f"📊 PV: {parsed_data['pv_total_power']:.2f}kW "
                        f"(Ost: {parsed_data['pv_east_power']:.2f}kW, West: {parsed_data['pv_west_power']:.2f}kW) | "
                        f"Batterie: {parsed_data['battery_soc']:.0f}% | "
                        f"Netz: {parsed_data['grid_power']:.2f}kW | "
                        f"Haus: {parsed_data['house_consumption']:.2f}kW"
                    )
                else:
                    logger.warning("⚠️ Unvollständige Daten vom Dongle erhalten")

            except Exception as e:
                logger.error(f"❌ Fehler beim Sammeln der Daten: {e}", exc_info=True)

            # Warten bis zum nächsten Poll
            await asyncio.sleep(settings.poll_interval)

        logger.info("🛑 Collector-Loop beendet")
