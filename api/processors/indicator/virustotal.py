"""VirusTotal API integration for TIP."""

import functools
import logging
import os
from typing import Any, cast

import vt as virustotal

from api.decorators.processor import processor
from api.processors.indicator.baseclass import TIPSource
from api.typings.models.indicators import Indicator, IndicatorType

logger = logging.getLogger(__name__)

@functools.cache
def _fetch_data_cache(
    indicator: str,
    indicator_type: IndicatorType,
) -> virustotal.Object:
    info = None
    vt = virustotal.Client(os.environ["VIRUSTOTAL_API_KEY"])
    try:
        match indicator_type:
            case IndicatorType.IP:
                info = vt.get_object(f"/ip_addresses/{indicator}")
            case IndicatorType.DOMAIN:
                info = vt.get_object(f"/domains/{indicator}")
            case IndicatorType.URL:
                info = vt.get_object(f"/urls/{indicator}")
            case IndicatorType.HASH:
                info = vt.get_object(f"/files/{indicator}")
    except virustotal.error.APIError as e:
        vt.close()
        logger.debug(e)
        if e.code == "NotFoundError":
            return {
                "error": "Indicator not found in VirusTotal, did you specify the right type?",  # noqa: E501
            }

    vt.close()
    return info


@processor(
    indicator_types=[
        IndicatorType.IP,
        IndicatorType.DOMAIN,
        IndicatorType.URL,
        IndicatorType.HASH,
    ],
)
class VirusTotal(TIPSource):
    """The class responsible for fetching information from VirusTotal."""

    def __init__(self) -> None:
        """Initialize the VirusTotal API client."""
        self.processor_name = "VirusTotal"

    def fetch_data(self, indicator: Indicator) -> dict[str, Any]:
        """Fetch information from VirusTotal based on the target type.

        Args:
        ----
            indicators: A list of indicators to fetch information about, each
            indicator is a dictionary containing the indicator type and the
            indicator value.

        """
        info = _fetch_data_cache(indicator.value, indicator.type)

        if not info:
            return {}
        if info.get("error"):
            return cast(dict[str, str], info)

        useful_keys = [
            "whois",
            "continent",
            "meaningful_name",
            "creation_date",
            "last_submission_date",
        ]

        full_info = {}

        for key in useful_keys:
            value = info.get(key)
            if value:
                full_info[key] = value

        full_info["last_analysis_stats"] = dict(info.get("last_analysis_stats"))

        engine_names = list(info.get("last_analysis_results").keys())

        # get the first 10 engines instead of all of them to reduce context.
        engine_names_to_process = engine_names[:10]

        for engine_name in engine_names_to_process:
            engine_info = info.get("last_analysis_results").get(engine_name)
            full_info[f"engine_{engine_name}_method"] = engine_info["method"]
            full_info[f"engine_{engine_name}_category"] = engine_info["category"]
            full_info[f"engine_{engine_name}_result"] = engine_info["result"]

        return full_info
