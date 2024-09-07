from api.exceptions.indicator_exceptions import InvalidIndicatorTypeError
from api.processors.indicator.baseclass import TIPSource
from api.typings.models.indicators import IndicatorType


class ProcessorRegistry:
    def __init__(self) -> None:
        self.processor_registry: dict[IndicatorType, list[type[TIPSource]]] = {}

    def register(
        self,
        indicator_types: list[IndicatorType],
        cls: type[TIPSource],
    ) -> None:
        for indicator_type in indicator_types:
            if not isinstance(indicator_type, IndicatorType):
                raise InvalidIndicatorTypeError

            if indicator_type not in self.processor_registry:
                self.processor_registry[indicator_type] = [cls]
            else:
                self.processor_registry[indicator_type].append(cls)

    def get_processor(self, indicator_type: IndicatorType) -> list[type[TIPSource]]:
        return self.processor_registry.get(indicator_type, [])


processor_registry = ProcessorRegistry()
