import functools
import os
from typing import Any, Literal

import vt as Vt

from api.tipsource.baseclass import TIPSource

@functools.cache
def _fetch_data_cache(vt: Vt.Client, target: str, target_type: Literal['ip', 'domain', 'url', 'hash']) -> Vt.Object:
    info = None
    match target_type:
        case "ip":
            info = vt.get_object(f"/ip-addresses/{target}")
        case "domain":
            info = vt.get_object(f"/domains/{target}")
        case "url":
            info = vt.get_object(f"/urls/{target}")
        case "hash":
            info = vt.get_object(f"/files/{target}")

    return info


class VirusTotal(TIPSource):
    def __init__(self) -> None:
        self.vt = Vt.Client(os.environ["VIRUSTOTAL_API_KEY"])

        # have no clue how to type kwargs in subclass like this
    def fetch_data(self, queries: list[str], **kwargs: Any) -> dict[str, Any]:
        """Fetch information from VirusTotal based on the target type.

        Args:
        ----
            queries: A list of targets to fetch information about
            target_type: The type of target to fetch information
            about, must be one of ip, domain, url, hash

        """
        target_type = kwargs.get(
            "target_type", "hash",
        )  # hash by default for virustotal
        full_info: dict[str, dict[str, str | dict[str, Any]]] = {}

        for target in queries:
            info = _fetch_data_cache(self.vt, target, target_type)

            if not info:
                full_info[target] = {}
                continue

            useful_keys = [
                "whois",
                "continent",
                "meaningful_name",
                "creation_date",
                "last_submission_date",
            ]

            final_info = {}

            for key in useful_keys:
                value = info.get(key)
                if value:
                    final_info[key] = value

            final_info["last_analysis_stats"] = dict(info.get("last_analysis_stats"))

            engine_names = list(info.get("last_analysis_results").keys())

            # get the first 10 engines instead of all of them to reduce context.
            engine_names_to_process = engine_names[:10]

            for engine_name in engine_names_to_process:
                engine_info = info.get("last_analysis_results").get(engine_name)
                final_info[f"engine_{engine_name}_method"] = engine_info["method"]
                final_info[f"engine_{engine_name}_category"] = engine_info["category"]
                final_info[f"engine_{engine_name}_result"] = engine_info["result"]

                full_info["target"] = final_info

        return full_info
