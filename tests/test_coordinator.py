"""Tests for the OSMGeocodeCoordinator."""

from unittest.mock import patch

import pytest
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.osm_geocode.const import (
    CONF_SCAN_INTERVAL,
    CONF_SOURCE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from custom_components.osm_geocode.coordinator import OSMGeocodeCoordinator


@pytest.fixture
def coordinator(hass):
    """Create a coordinator with a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_SOURCE: "device_tracker.test", "name": "Test"},
        options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
    )
    return OSMGeocodeCoordinator(hass, entry)


async def test_successful_fetch(
    hass: HomeAssistant, coordinator, nominatim_response
):
    """Coordinator returns address dict on successful fetch."""
    hass.states.async_set(
        "device_tracker.test",
        "home",
        {ATTR_LATITUDE: 52.2297, ATTR_LONGITUDE: 21.0122},
    )

    flat = nominatim_response["features"][0]["properties"].copy()
    flat.update(flat.pop("address"))

    with patch(
        "custom_components.osm_geocode.coordinator.get_address",
        return_value=flat,
    ):
        data = await coordinator._async_update_data()

    assert data["road"] == "Test Road"
    assert data["latitude"] == 52.2297
    assert data["zone"] == "home"


async def test_source_entity_not_found(
    hass: HomeAssistant, coordinator
):
    """Coordinator raises UpdateFailed when source entity missing."""
    with pytest.raises(UpdateFailed, match="not found"):
        await coordinator._async_update_data()


async def test_no_coordinates(hass: HomeAssistant, coordinator):
    """Coordinator raises UpdateFailed when entity has no lat/lon."""
    hass.states.async_set("device_tracker.test", "home", {})
    with pytest.raises(UpdateFailed, match="no location"):
        await coordinator._async_update_data()


async def test_api_error(hass: HomeAssistant, coordinator):
    """Coordinator raises UpdateFailed on API error."""
    hass.states.async_set(
        "device_tracker.test",
        "home",
        {ATTR_LATITUDE: 52.0, ATTR_LONGITUDE: 21.0},
    )

    with (
        patch(
            "custom_components.osm_geocode.coordinator.get_address",
            side_effect=ValueError("API error"),
        ),
        pytest.raises(UpdateFailed, match="API error"),
    ):
        await coordinator._async_update_data()
