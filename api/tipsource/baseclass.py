from abc import ABC, abstractmethod
from typing import Any


class TIPSource(ABC):
    @abstractmethod
    def fetch_data(self, queries: list[str], **kwargs: Any) -> dict[str, Any]:
        """Fetch information from Threat Intelligence Platform based on
        the query/target, including any additional parameters.

        Args:
        ----
            queries: A list of queries or targets to fetch information about
            **kwargs: Additional parameters to pass to the fetcher

        """
