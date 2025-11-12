from . import oauthbot
from .zhigenie import handleRequest, makeResponse

import logging
_LOGGER = logging.getLogger(__name__)


class geniebot(oauthbot):
    """ZhiBot genie platform with optional Long-Lived Token support"""

    def __init__(self, botname, hass, conf):
        # Check for long-lived token configuration
        self.ll_token = conf.get('long_lived_token')
        self.ll_token_file = conf.get('long_lived_token_file')

        # Initialize with or without OAuth based on config
        if self.ll_token or self.ll_token_file:
            # Long-Lived Token mode: Don't trigger OAuth patching
            from . import basebot
            basebot.__init__(self, botname, hass, conf)
            _LOGGER.info("ZhiBot genie: Long-Lived Token mode (NO OAuth patch)")
        else:
            # OAuth mode: Normal initialization (includes OAuth patching)
            super().__init__(botname, hass, conf)
            _LOGGER.info("ZhiBot genie: OAuth mode")

    def init_auth(self, botname):
        """
        Override to prevent OAuth patching when using long-lived tokens
        """
        # If using long-lived token, skip OAuth patching
        if self.ll_token or self.ll_token_file:
            from . import basebot
            basebot.init_auth(self, botname)
            _LOGGER.debug("Skipped OAuth patching (Long-Lived Token mode)")
        else:
            # Normal OAuth patching
            super().init_auth(botname)

    async def async_check_auth(self, data):
        """
        Authentication with dual mode support
        """
        if self.ll_token or self.ll_token_file:
            # Long-Lived Token mode: Validate directly
            token = data['payload']['accessToken']
            return await self.hass.auth.async_validate_access_token(token) is not None
        else:
            # OAuth mode: Use OAuth validation
            return await self.async_check_token(data['payload']['accessToken'])

    async def async_handle(self, data):
        return await handleRequest(self.hass, data)

    def response(self, result):
        if isinstance(result, str):
            return makeResponse('ACCESS_TOKEN_INVALIDATE' if result == '没有访问授权！' else 'SERVICE_ERROR')
        return result

    async def post(self, request):
        """
        POST handler for manual authentication
        """
        try:
            data = await request.json()
            _LOGGER.info("REQUEST: %s", data)

            if await self.async_check_auth(data):
                result = await self.async_handle(data)
            else:
                result = "没有访问授权！"

            _LOGGER.debug("RESPONSE: %s", result)
        except Exception as e:
            result = repr(e)
            import traceback
            _LOGGER.error(traceback.format_exc())

        return self.json(self.response(result))
