"""Nominatim API client for OSM Geocode."""

import requests

from .const import NOMINATIM_URL


def get_address(latitude, longitude):
    """Reverse geocode coordinates using OpenStreetMap Nominatim."""
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
