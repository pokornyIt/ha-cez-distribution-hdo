"""Config flow for CEZ Distribution HDO integration."""

from __future__ import annotations

import re
from typing import Any, cast

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from cez_distribution_hdo import TariffService, sanitize_signal_for_entity

from .const import CONF_EAN, CONF_PREFIX, CONF_SIGNAL, DEFAULT_PREFIX, DOMAIN

EAN_RE = re.compile(r"^8591824\d\d[45678]\d{8}$")
PREFIX_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$")  # max 32 chars


class CezDistributionHdoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            ean = cast(str, user_input[CONF_EAN]).strip()
            prefix = cast(str, user_input.get(CONF_PREFIX, DEFAULT_PREFIX)).strip()

            if not EAN_RE.match(ean):
                errors[CONF_EAN] = "invalid_ean"

            if prefix and not PREFIX_RE.match(prefix):
                errors[CONF_PREFIX] = "invalid_prefix"

            if not errors:
                try:
                    tz = self.hass.config.time_zone
                    service = TariffService(tz_name=tz or "UTC")
                    await service.refresh(ean=ean)
                    signals = list(service.signals)
                except Exception:
                    errors["base"] = "cannot_connect"
                else:
                    if not signals:
                        errors["base"] = "no_signals"
                    else:
                        self.context["ean"] = ean  # type: ignore
                        self.context["prefix"] = prefix  # type: ignore
                        self.context["signals"] = signals  # type: ignore
                        return await self.async_step_signal()

        schema = vol.Schema(
            {
                vol.Required(CONF_EAN): cv.string,
                vol.Optional(CONF_PREFIX, default=DEFAULT_PREFIX): cv.string,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_signal(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        ean = cast(str, self.context["ean"])  # type: ignore
        prefix = cast(str, self.context.get("prefix", DEFAULT_PREFIX))
        signals = cast(list[str], self.context["signals"])  # type: ignore

        if user_input is not None:
            signal = cast(str, user_input[CONF_SIGNAL])

            # Unique config entry per (EAN + signal)
            await self.async_set_unique_id(f"{ean}:{signal}")
            self._abort_if_unique_id_configured()

            data = {
                CONF_EAN: ean,
                CONF_SIGNAL: signal,
            }
            options = {
                CONF_PREFIX: prefix,
            }

            # Avoid putting full EAN into the entry title (keep it simple)
            # sig = sanitize_signal_for_entity(signal)  # a1b4pd04 -> a1b4pd04 (sanitized)
            prefix = prefix or DEFAULT_PREFIX
            title = f"{prefix}"
            return self.async_create_entry(title=title, data=data, options=options)

        schema = vol.Schema({vol.Required(CONF_SIGNAL): vol.In(signals)})

        return self.async_show_form(step_id="signal", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return CezDistributionHdoOptionsFlow(config_entry)


class CezDistributionHdoOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            prefix = cast(str, user_input.get(CONF_PREFIX, "")).strip()

            if prefix and not PREFIX_RE.match(prefix):
                errors[CONF_PREFIX] = "invalid_prefix"
            else:
                return self.async_create_entry(title="", data={CONF_PREFIX: prefix})

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_PREFIX,
                    default=self.entry.options.get(CONF_PREFIX, ""),
                ): cv.string,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
