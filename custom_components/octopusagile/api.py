"""Async API client for OctopusAgile (aiohttp, modernized)."""
import logging
from datetime import datetime
import collections

_LOGGER = logging.getLogger(__name__)

class OctopusAgileApiClient:
    def __init__(self, session, region_code, api_key, mpan, serial):
        self._session = session
        self._region_code = region_code
        self._api_key = api_key
        self._mpan = mpan
        self._serial = serial
        self._base_url = 'https://api.octopus.energy/v1'

    async def async_get_rates(self, date_from=None, date_to=None):
        url = f"{self._base_url}/products/AGILE-18-02-21/electricity-tariffs/E-1R-AGILE-18-02-21-{self._region_code}/standard-unit-rates/"
        params = {}
        if date_from:
            params['period_from'] = date_from
        if date_to:
            params['period_to'] = date_to
        headers = {"Authorization": f"Basic {self._api_key}"}
        async with self._session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            date_rates = collections.OrderedDict()
            for result in data.get("results", []):
                price = result["value_inc_vat"]
                valid_from = result["valid_from"]
                date_rates[valid_from] = price
            return date_rates

    async def async_get_consumption(self, start, end):
        url = f"{self._base_url}/electricity-meter-points/{self._mpan}/meters/{self._serial}/consumption/"
        params = {
            "period_from": f"{start}T00:00:00Z",
            "period_to": f"{end}T23:59:59Z",
            "order_by": "period"
        }
        headers = {"Authorization": f"Basic {self._api_key}"}
        async with self._session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
