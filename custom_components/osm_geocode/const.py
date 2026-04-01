"""Constants for the OSM Geocode integration."""

DOMAIN = "osm_geocode"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

CONF_SOURCE = "source"
CONF_TEMPLATE = "template"
CONF_ICON = "icon"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_ICON = "mdi:map-marker"
DEFAULT_SCAN_INTERVAL = 60

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
