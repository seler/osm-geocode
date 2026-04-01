"""Config flow for OSM Geocode integration."""

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    CONF_ICON,
    CONF_SCAN_INTERVAL,
    CONF_SOURCE,
    CONF_TEMPLATE,
    DEFAULT_ICON,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class OSMGeocodeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OSM Geocode."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"osm_geocode_{user_input[CONF_SOURCE]}"
            )
            self._abort_if_unique_id_configured()

            entity = self.hass.states.get(user_input[CONF_SOURCE])
            if entity is None:
                errors[CONF_SOURCE] = "source_not_found"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_SOURCE: user_input[CONF_SOURCE],
                        CONF_NAME: user_input[CONF_NAME],
                    },
                    options={
                        CONF_TEMPLATE: "",
                        CONF_ICON: DEFAULT_ICON,
                        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="device_tracker")
                ),
                vol.Required(CONF_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(
        self, import_data: dict
    ) -> ConfigFlowResult:
        """Handle import from YAML configuration."""
        await self.async_set_unique_id(
            f"osm_geocode_{import_data[CONF_SOURCE]}"
        )
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=import_data.get(CONF_NAME, "OSM Geocode"),
            data={
                CONF_SOURCE: import_data[CONF_SOURCE],
                CONF_NAME: import_data.get(CONF_NAME, "OSM Geocode"),
            },
            options={
                CONF_TEMPLATE: import_data.get(CONF_TEMPLATE, ""),
                CONF_ICON: import_data.get(CONF_ICON, DEFAULT_ICON),
                CONF_SCAN_INTERVAL: import_data.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            },
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> "OSMGeocodeOptionsFlow":
        """Get the options flow for this handler."""
        return OSMGeocodeOptionsFlow()


class OSMGeocodeOptionsFlow(OptionsFlow):
    """Handle options flow for OSM Geocode."""

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_TEMPLATE,
                    default=options.get(CONF_TEMPLATE, ""),
                ): str,
                vol.Optional(
                    CONF_ICON,
                    default=options.get(CONF_ICON, DEFAULT_ICON),
                ): selector.IconSelector(),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(int, vol.Range(min=10, max=3600)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
