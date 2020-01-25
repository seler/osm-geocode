# Reverse Geocoding Sensor for Home Assistant

Reverse geocoding generates an address from a latitude and longitude of device tracker.

Inspired by [GoogleGeocode-HASS](https://github.com/michaelmcarthur/GoogleGeocode-HASS).

![osmgeocodeui1](https://github.com/seler/osm-geocode/blob/master/osmgeocodeui1.png 'Screenshot')

![osmgeocodeui2](https://github.com/seler/osm-geocode/blob/master/osmgeocodeui2.png 'Screenshot')

### Installation:

#### HACS

- Add custom repository in HACS settings tab. Select `Integration` category.
- Search for and install the "OSM Geocode" integration.
- Restart Home Assistant.

#### Manual installation

- Copy `custom_components` into the config directory of your Home Assistant installation.
- Restart Home Assistant.

### Configuration

```
sensor:
  - platform: osm_geocode
    name: Location Sensor Name
    source: device_tracker.source_device_tracker
```

#### Configuration variables:

`source` _(Required)_: device_tracker that produces latitude and longitude

`name` _(Required)_: A name to display on the sensor


`scan_interval` _(Optional)_: The frequency of scan in seconds. Default: `60`.

`icon` _(Optional)_: Icon to display. Default: `"mdi:map-marker"`.

`template` _(Optional)_:
    Possible attributes: `category`, `type`, `importance`, `addresstype`, `name`, `display_name`, `address`, `house_number`, `road`, `city_district`, `city`, `county`, `state`, `postcode`, `country`, `country_code`, 
    Default: `"{% if name %} {{ name }}, {% endif %} {{ house_number }} {{ road }}, {{ city_district }}, {{ city }}"` 
