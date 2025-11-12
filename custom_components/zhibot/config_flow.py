"""Config flow for ZhiBot."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_NAME

from . import DOMAIN

class ZhiBotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ZhiBot."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check if this name already exists
            name = user_input[CONF_NAME]
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                if entry.data.get(CONF_NAME) == name:
                    return self.async_show_form(
                        step_id="user",
                        data_schema=vol.Schema({
                            vol.Required("platform", default=user_input.get("platform", "genie")): vol.In({
                                "genie": "天猫精灵 (AliGenie) - IoT技能",
                                "genie2": "天猫精灵个人技能 (AliGenie2) - 聊天AI",
                                "miai": "小爱同学 (XiaoAi)",
                                "ding": "钉钉 (DingTalk)",
                            }),
                            vol.Required(CONF_NAME, default=name): str,
                            vol.Optional("long_lived_token", default=""): str,
                            vol.Optional("long_lived_token_file", default=""): str,
                            vol.Optional("token", description="传统OAuth令牌（不推荐）"): str,
                        }),
                        errors={CONF_NAME: "already_configured"},
                    )

            return self.async_create_entry(
                title=name,
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Required("platform", default="genie"): vol.In({
                "genie": "天猫精灵 (AliGenie) - IoT技能",
                "genie2": "天猫精灵个人技能 (AliGenie2) - 聊天AI",
                "miai": "小爱同学 (XiaoAi)",
                "ding": "钉钉 (DingTalk)",
            }),
            vol.Required(CONF_NAME, default="tmall"): str,
            vol.Optional("long_lived_token", default=""): str,
            vol.Optional("long_lived_token_file", default=""): str,
            vol.Optional("token", description="传统OAuth令牌（不推荐）"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Options flow handler."""
        return ZhiBotOptionsFlow(config_entry)

class ZhiBotOptionsFlow(config_entries.OptionsFlow):
    """Options flow for ZhiBot."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        # HA automatically sets self.config_entry, don't assign explicitly

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage options."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Optional(
                "long_lived_token",
                default=self.config_entry.options.get("long_lived_token", "")
            ): str,
            vol.Optional(
                "long_lived_token_file",
                default=self.config_entry.options.get("long_lived_token_file", "")
            ): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
