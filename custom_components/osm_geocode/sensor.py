"""Reverse Geocoding sensor based on OSM Nominatim."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import template as templater

from .const import (
    CONF_ICON,
    CONF_SOURCE,
    CONF_TEMPLATE,
    DEFAULT_ICON,
    DEFAULT_TEMPLATE,
    DOMAIN,
)
from .coordinator import OSMGeocodeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OSM Geocode sensor from a config entry."""
    coordinator: OSMGeocodeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OSMGeocodeSensor(coordinator, entry)])


# --- YAML backward compatibility (deprecated) ---

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import YAML configuration into config entries (deprecated)."""
    _LOGGER.warning(
        "Configuration of osm_geocode via YAML is deprecated and will be "
        "removed in a future version. Please use the UI to configure this "
        "integration"
    )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data=dict(config),
        )
    )


# --- Sensor entity ---

class OSMGeocodeSensor(CoordinatorEntity, SensorEntity):
    """Representation of an OSM Geocode sensor."""

    def __init__(
        self,
        coordinator: OSMGeocodeCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"osm_geocode_{entry.data[CONF_SOURCE]}"
        self._attr_name = entry.data.get(CONF_NAME)

    @property
    def native_value(self) -> str:
        """Return the rendered address template as the sensor state."""
        if self.coordinator.data is None:
            return None
        template_str = (
            self._entry.options.get(CONF_TEMPLATE, "") or DEFAULT_TEMPLATE
        )
        return templater.Template(template_str, self.hass).async_render(
            self.coordinator.data
        )

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._entry.options.get(CONF_ICON, DEFAULT_ICON)

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return address attributes."""
        return self.coordinator.data
