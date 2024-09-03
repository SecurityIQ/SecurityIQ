from abc import ABC, abstractmethod
from typing import _TypedDict, Any, Generic, TypeVar, Union, Unpack

class TIPSource(ABC):
    @abstractmethod
    def fetch_data(self, queries: list[str], **kwargs: Any) -> dict[str, Any]:
        """ Fetch information from Threat Intelligence Platform based on the query/target, including any additional parameters """
        pass

