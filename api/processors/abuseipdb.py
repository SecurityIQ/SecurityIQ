import functools
import os
from typing import Any, cast

import requests

from api.decorators.processor import processor
from api.processors.baseclass import TIPSource
from api.typings.models.indicators import Indicator, IndicatorType


@functools.cache
def _fetch_data_cache(ip: str) -> dict[str, Any]:
    req_headers = {
        "Accept": "application/json",
        "Key": os.environ["ABUSEIPDB_API_KEY"],
    }
    base_url = "https://api.abuseipdb.com/api/v2/check?ipAddress={}"
    response = requests.get(base_url.format(ip), headers=req_headers, timeout=5)

    if response.ok:
        return cast(dict[str, Any], response.json())

    return {}


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

        response = _fetch_data_cache(ip)["data"]
        return {
            "abuseConfidenceScore": response["abuseConfidenceScore"],
            "countryCode": response["countryCode"],
            "isp": response["isp"],
            "domain": response["domain"],
            "isTor": response["isTor"],
            "totalReports": response["totalReports"],
        }
