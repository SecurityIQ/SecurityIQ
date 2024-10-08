import functools
import logging
import os
from typing import Any, cast

import requests

from api.decorators.processor import processor
from api.processors.enrich.baseclass import TIPSource
from api.typings.models.indicators import Indicator, IndicatorType

logger = logging.getLogger(__name__)


@functools.cache
def _fetch_data_cache(ip: str) -> dict[str, Any]:
    req_headers = {
        "Accept": "application/json",
        "Key": os.environ["ABUSEIPDB_API_KEY"],
    }
    base_url = "https://api.abuseipdb.com/api/v2/check?ipAddress={}"
    response = requests.get(base_url.format(ip), headers=req_headers, timeout=5)

    return cast(dict[str, Any], response.json())


@processor(indicator_types=[IndicatorType.IP])
class AbuseIPDB(TIPSource):
    def __init__(self) -> None:
        self.processor_name = "AbuseIPDB"

    def fetch_data(self, indicator: Indicator) -> dict[str, Any]:
        """Fetch reported IP addresses information from AbuseIPDB.

        Args:
        ----
            indicators: A list of indicators to fetch information about, each
            indicator is a dictionary containing the indicator type and the
            indicator value.

        """
        ip = indicator.value

        response = _fetch_data_cache(ip)

        if response.get("errors"):
            logger.debug(response)
            return response
        if not response.get("data"):
            return {}
        response = response["data"]

        return {
            "abuseConfidenceScore": response["abuseConfidenceScore"],
            "countryCode": response["countryCode"],
            "isp": response["isp"],
            "domain": response["domain"],
            "isTor": response["isTor"],
            "totalReports": response["totalReports"],
        }
