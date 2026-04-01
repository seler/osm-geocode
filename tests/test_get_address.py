"""Tests for the get_address function."""

import pytest
import requests
import requests_mock as rm

from custom_components.osm_geocode.api import get_address
from custom_components.osm_geocode.const import NOMINATIM_URL


def test_get_address_returns_flattened_address(nominatim_response):
    """Successful geocoding returns address with nested 'address' key flattened."""
    with rm.Mocker() as m:
        m.get(NOMINATIM_URL, json=nominatim_response)
        result = get_address(52.2297, 21.0122)

    assert result["road"] == "Test Road"
    assert result["house_number"] == "1"
    assert result["city"] == "Test City"
    assert result["name"] == "Test Place"
    assert "address" not in result


def test_get_address_raises_on_empty_features():
    """ValueError when Nominatim returns no features."""
    with rm.Mocker() as m:
        m.get(NOMINATIM_URL, json={"features": []})
        with pytest.raises(ValueError, match="No features"):
            get_address(52.2297, 21.0122)


def test_get_address_raises_on_http_error():
    """HTTPError propagated on server errors."""
    with rm.Mocker() as m:
        m.get(NOMINATIM_URL, status_code=500)
        with pytest.raises(requests.HTTPError):
            get_address(52.2297, 21.0122)


def test_get_address_raises_on_connection_error():
    """ConnectionError propagated on network failures."""
    with rm.Mocker() as m:
        m.get(NOMINATIM_URL, exc=requests.ConnectionError("timeout"))
        with pytest.raises(requests.ConnectionError):
            get_address(52.2297, 21.0122)
