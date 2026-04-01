"""Reverse Geocoding based on OSM Nominatim."""

import logging
from datetime import timedelta

import requests
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE, CONF_NAME
from homeassistant.helpers import template as templater
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

__version__ = "0.2.0"
_LOGGER = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

CONF_SOURCE = "source"
CONF_TEMPLATE = "template"
CONF_ICON = "icon"

DEFAULT_ICON = "mdi:map-marker"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SOURCE): cv.entity_id,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_TEMPLATE): cv.string,
        vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
    }
)


def get_address(latitude, longitude):
    headers = {
        "user-agent": "OSM Geocode HASS",
    }

    params = (
        ("lat", latitude),
        ("lon", longitude),
        ("format", "geojson"),
    )

    response = requests.get(
        NOMINATIM_URL, headers=headers, params=params, timeout=10
    )
    response.raise_for_status()

    data = response.json()
    features = data.get("features")
    if not features:
        raise ValueError("No features returned from Nominatim")

    address = features[0]["properties"].copy()
    address.update(address["address"])
    del address["address"]
    return address


DEFAULT_TEMPLATE = """\
{% if zone %}\
{{ zone }}\
{% else %}\
{% if name %}\
{{ name }}, \
{% endif %}\
{{ house_number }} {{ road }}, \
{{ city_district }}, {{ city }}\
{% endif %}"""


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([OSMGeocodeSensor(hass, config)])


class OSMGeocodeSensor(Entity):
    def __init__(self, hass, config):
        self.hass = hass
        self.address = None
        self.config = config
        self._state = "Loading..."

    @Throttle(timedelta(seconds=60))
    async def async_update(self):
        source = self.config.get(CONF_SOURCE)
        entity = self.hass.states.get(source)

        if entity is None:
            _LOGGER.warning("Entity %s not found", source)
            return

        latitude = entity.attributes.get(ATTR_LATITUDE)
        longitude = entity.attributes.get(ATTR_LONGITUDE)

        if latitude is None or longitude is None:
            _LOGGER.warning(
                "Entity %s has no location attributes", source
            )
            return

        try:
            self.address = await self.hass.async_add_executor_job(
                get_address, latitude, longitude
            )
        except (requests.RequestException, ValueError, KeyError) as err:
            _LOGGER.error("Error fetching address: %s", err)
            return

        self.address.update(
            {"zone": entity.state, "latitude": latitude, "longitude": longitude}
        )

        template = self.config.get(CONF_TEMPLATE, DEFAULT_TEMPLATE)
        self._state = templater.Template(template, self.hass).render(self.address)

    @property
    def name(self):
        return self.config.get(CONF_NAME)

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self.config.get(CONF_ICON, DEFAULT_ICON)

    @property
    def extra_state_attributes(self):
        return self.address
