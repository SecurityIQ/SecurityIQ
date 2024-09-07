from abc import ABC, abstractmethod
from typing import Any

from api.typings.models.indicators import Indicator


class TIPSource(ABC):
    """Base class for Threat Intelligence Platform sources."""

    def __init__(self) -> None:
        self.processor_name = ""

    @abstractmethod
    def fetch_data(self, indicator: Indicator) -> dict[str, Any]:
        """Fetch information from Threat Intelligence Platform.

        Fetch information from TIPs based on the indicator

        Args:
        ----
            indicator: An indicator to fetch information about,
            Indicator is a dictionary containing the indicator
            type and the indicator value.

        """
