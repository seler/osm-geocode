"""Tests for the config flow."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
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


async def test_user_flow_creates_entry(hass: HomeAssistant):
    """User flow: happy path creates a config entry."""
    hass.states.async_set("device_tracker.phone", "home", {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "source": "device_tracker.phone",
            "name": "My Location",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["source"] == "device_tracker.phone"
    assert result["data"]["name"] == "My Location"
    assert result["options"]["icon"] == DEFAULT_ICON
    assert result["options"]["scan_interval"] == DEFAULT_SCAN_INTERVAL


async def test_user_flow_source_not_found(hass: HomeAssistant):
    """User flow: error when source entity does not exist."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "source": "device_tracker.nonexistent",
            "name": "Test",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["source"] == "source_not_found"


async def test_user_flow_duplicate_aborts(hass: HomeAssistant):
    """User flow: abort when same source already configured."""
    existing = MockConfigEntry(
        domain=DOMAIN,
        data={"source": "device_tracker.phone", "name": "Existing"},
        unique_id="osm_geocode_device_tracker.phone",
    )
    existing.add_to_hass(hass)

    hass.states.async_set("device_tracker.phone", "home", {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "source": "device_tracker.phone",
            "name": "Duplicate",
        },
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_import_flow_creates_entry(hass: HomeAssistant):
    """YAML import creates a config entry with correct data."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "import"},
        data={
            "source": "device_tracker.phone",
            "name": "Imported",
            "icon": "mdi:home",
            "template": "{{ city }}",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["source"] == "device_tracker.phone"
    assert result["options"]["icon"] == "mdi:home"
    assert result["options"]["template"] == "{{ city }}"


async def test_options_flow(hass: HomeAssistant):
    """Options flow: change template and scan_interval."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"source": "device_tracker.phone", "name": "Test"},
        options={
            "template": "",
            "icon": DEFAULT_ICON,
            "scan_interval": DEFAULT_SCAN_INTERVAL,
        },
        unique_id="osm_geocode_device_tracker.phone",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "template": "{{ road }}, {{ city }}",
            "icon": "mdi:home",
            "scan_interval": 120,
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options["template"] == "{{ road }}, {{ city }}"
    assert entry.options["icon"] == "mdi:home"
    assert entry.options["scan_interval"] == 120
