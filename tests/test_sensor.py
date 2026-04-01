"""Tests for the OSMGeocodeSensor with config entries."""

from unittest.mock import patch

import pytest
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.osm_geocode.const import (
    CONF_ICON,
    CONF_SCAN_INTERVAL,
    CONF_SOURCE,
    CONF_TEMPLATE,
    DEFAULT_ICON,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


@pytest.fixture
def mock_config_entry(hass):
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_SOURCE: "device_tracker.test",
            CONF_NAME: "Test Geocode",
        },
        options={
            CONF_TEMPLATE: "",
            CONF_ICON: DEFAULT_ICON,
            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        },
        unique_id="osm_geocode_device_tracker.test",
    )
    entry.add_to_hass(hass)
    return entry


async def test_sensor_setup_from_config_entry(
    hass: HomeAssistant, mock_config_entry, nominatim_response
):
    """Sensor is created from a config entry and shows address."""
    hass.states.async_set(
        "device_tracker.test",
        "not_home",
        {ATTR_LATITUDE: 52.2297, ATTR_LONGITUDE: 21.0122},
    )

    flat = nominatim_response["features"][0]["properties"].copy()
    flat.update(flat.pop("address"))

    with patch(
        "custom_components.osm_geocode.coordinator.get_address",
        return_value=flat,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("sensor.test_geocode")
    assert state is not None
    assert state.state != "unknown"
    assert state.attributes["latitude"] == 52.2297
    assert state.attributes["longitude"] == 21.0122
    assert state.attributes["zone"] == "not_home"


async def test_sensor_icon_from_options(
    hass: HomeAssistant, mock_config_entry, nominatim_response
):
    """Sensor uses icon from options."""
    hass.states.async_set(
        "device_tracker.test",
        "home",
        {ATTR_LATITUDE: 52.0, ATTR_LONGITUDE: 21.0},
    )
    flat = nominatim_response["features"][0]["properties"].copy()
    flat.update(flat.pop("address"))

    with patch(
        "custom_components.osm_geocode.coordinator.get_address",
        return_value=flat,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("sensor.test_geocode")
    assert state.attributes["icon"] == DEFAULT_ICON


async def test_sensor_unique_id(
    hass: HomeAssistant, mock_config_entry, nominatim_response
):
    """Sensor has a unique_id based on source entity."""
    hass.states.async_set(
        "device_tracker.test",
        "home",
        {ATTR_LATITUDE: 52.0, ATTR_LONGITUDE: 21.0},
    )
    flat = nominatim_response["features"][0]["properties"].copy()
    flat.update(flat.pop("address"))

    with patch(
        "custom_components.osm_geocode.coordinator.get_address",
        return_value=flat,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    from homeassistant.helpers import entity_registry as er
    entity_registry = er.async_get(hass)
    entry = entity_registry.async_get("sensor.test_geocode")
    assert entry is not None
    assert entry.unique_id == "osm_geocode_device_tracker.test"
