import functools
import os
from typing import Any

import requests

from api.tipsource.baseclass import TIPSource


class AbuseIPDB(TIPSource):
    def __init__(self) -> None:
        self.base_url = "https://api.abuseipdb.com/api/v2/check?ipAddress={}"
        self.req_headers = {
            "Accept": "application/json",
            "Key": os.environ["ABUSEIPDB_API_KEY"],
        }

    @functools.cache
    def _fetch_data_cache(self, ip: str) -> dict[str, Any]:
        response = requests.get(self.base_url.format(ip), headers=self.req_headers)

        if response.ok:
            return response.json()

        return {}

    # have no clue how to type kwargs in subclass like this
    def fetch_data(self, queries: list[str], **kwargs: Any) -> dict[str, Any]:
        full_info = {}
        for ip in queries:
            response = self._fetch_data_cache(ip)["data"]
            full_info["ipAddress"] = {
                "abuseConfidenceScore": response["abuseConfidenceScore"],
                "countryCode": response["countryCode"],
                "isp": response["isp"],
                "domain": response["domain"],
                "isTor": response["isTor"],
                "totalReports": response["totalReports"],
            }
        return full_info
