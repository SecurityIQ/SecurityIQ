import logging
from typing import Any

from api.registries.processor import processor_registry
from api.typings.models.indicators import Indicator


class ThreatAnalysis:
    def __init__(self) -> None: ...

    def analyse_threat(self, indicators: list[Indicator]) -> dict[str, Any]:
        all_info: dict[str, dict[str, dict[str, Any]]] = {}
        for indicator in indicators:
            processors = processor_registry.get_processor(indicator.type)
            logging.info(processors)
            for processor_cls in processors:
                processor = processor_cls()
                info = processor.fetch_data(indicator)
                all_info[indicator.value] = {}
                all_info[indicator.value][processor.processor_name] = info

        return all_info
