"""DataUpdateCoordinator for the Discovergy integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from pydiscovergy import Discovergy
from pydiscovergy.error import AccessTokenExpired, HTTPError
from pydiscovergy.models import Meter, Reading

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DiscovergyUpdateCoordinator(DataUpdateCoordinator[Reading]):
    """The Discovergy update coordinator."""

    config_entry: ConfigEntry
    discovergy_client: Discovergy
    meter: Meter

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        meter: Meter,
        discovergy_client: Discovergy,
    ) -> None:
        """Initialize the Discovergy coordinator."""
        self.config_entry = config_entry
        self.meter = meter
        self.discovergy_client = discovergy_client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> Reading:
        """Get last reading for meter."""
        try:
            return await self.discovergy_client.get_last_reading(
                self.meter.get_meter_id()
            )
        except AccessTokenExpired as err:
            raise ConfigEntryAuthFailed(
                f"Auth expired while fetching last reading for meter {self.meter.get_meter_id()}"
            ) from err
        except HTTPError as err:
            raise UpdateFailed(
                f"Error while fetching last reading for meter {self.meter.get_meter_id()}"
            ) from err
