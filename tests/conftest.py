"""Shared test fixtures for osm_geocode tests."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield

NOMINATIM_RESPONSE = {
    "features": [
        {
            "properties": {
                "name": "Test Place",
                "display_name": "Test Place, Test Road 1, Test City, Test Country",
                "address": {
                    "road": "Test Road",
                    "house_number": "1",
                    "city": "Test City",
                    "city_district": "Test District",
                    "country": "Test Country",
                },
            }
        }
    ]
}


@pytest.fixture
def nominatim_response():
    """Return a sample Nominatim GeoJSON response."""
    return NOMINATIM_RESPONSE
