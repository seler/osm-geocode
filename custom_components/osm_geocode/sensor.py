"""Reverse Geocoding based on OSM Nominatim."""
import logging
import typing
from datetime import timedelta

import requests
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.helpers import template as templater
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.location import has_location
from homeassistant.util import Throttle

__version__ = "0.1.0"
logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


def get_address(latitude, longitude):
    headers = {
        "user-agent": "OSM Geocode HASS",
    }

    params = (
        ("lat", latitude),
        ("lon", longitude),
        ("format", "geojson"),
    )

    response = requests.get(NOMINATIM_URL, headers=headers, params=params)

    address = response.json()["features"][0]["properties"].copy()
    address.update(address["address"])
    del address["address"]
    return address


DEFAULT_TEMPLATE = """
{% if name %}
    {{ name }},
{% endif %}
{{ house_number }} {{ road }},
{{ city_district }}, {{ city }}
"""


def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([OSMGeocodeSensor(hass, config)])


class OSMGeocodeSensor(Entity):
    def __init__(self, hass, config):
        self.hass = hass
        self.address = None
        self.config = config
        self._state = "Loading..."

    @Throttle(timedelta(seconds=60))
    def update(self):
        source = self.config.get("source")
        latitude, longitude = self._get_position(source)
        self.address = get_address(latitude, longitude)

        template = self.config.get("template", DEFAULT_TEMPLATE)
        self._state = templater.Template(template, self.hass).render(self.address)

    @property
    def name(self):
        return self.config.get("name")

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self.config.get("icon", "mdi:map-marker")

    @property
    def device_state_attributes(self):
        return self.address

    def _get_position(self, entity_id) -> typing.Optional[tuple]:
        entity = self.hass.states.get(entity_id)

        if has_location(entity):
            return (
                entity.attributes.get(ATTR_LATITUDE),
                entity.attributes.get(ATTR_LONGITUDE),
            )
