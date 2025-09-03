"""DataUpdateCoordinator for OctopusAgile integration (async, modernized)."""
import logging
from datetime import timedelta, datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


from .api import OctopusAgileApiClient

class OctopusAgileDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.config = config
        self.session = async_get_clientsession(hass)
        self.api = OctopusAgileApiClient(
            self.session,
            config["region_code"],
            config["api_key"],
            config["mpan"],
            config["serial"]
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} data",
            update_interval=timedelta(minutes=30),
        )

    async def _async_update_data(self):
        try:
            # Fetch rates for the next 24 hours
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            rates = await self.api.async_get_rates(date_from=now)
            # Optionally: fetch previous/current/next/min rates
            # For now, just return all rates
            return {
                "rates": rates,
                "previous": None,
                "current": None,
                "next": None,
                "min": min(rates.values()) if rates else None,
            }
        except Exception as err:
            raise UpdateFailed(f"Error updating OctopusAgile data: {err}")
