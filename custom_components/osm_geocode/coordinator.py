"""Data update coordinator for OSM Geocode."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import get_address
from .const import CONF_SCAN_INTERVAL, CONF_SOURCE, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class OSMGeocodeCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch address data from Nominatim."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._source = entry.data[CONF_SOURCE]
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=f"osm_geocode_{self._source}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Fetch latest address data."""
        entity = self.hass.states.get(self._source)
        if entity is None:
            raise UpdateFailed(f"Source entity {self._source} not found")

        latitude = entity.attributes.get(ATTR_LATITUDE)
        longitude = entity.attributes.get(ATTR_LONGITUDE)
        if latitude is None or longitude is None:
            raise UpdateFailed(
                f"Entity {self._source} has no location attributes"
            )

        try:
            address = await self.hass.async_add_executor_job(
                get_address, latitude, longitude
            )
        except Exception as err:
            raise UpdateFailed(f"Error fetching address: {err}") from err

        address.update(
            {"zone": entity.state, "latitude": latitude, "longitude": longitude}
        )
        return address
