from collections.abc import Callable

from api.exceptions.indicator_exceptions import InvalidIndicatorTypeError
from api.processors.baseclass import TIPSource
from api.registries.processor import processor_registry
from api.typings.models.indicators import IndicatorType


def processor(
    indicator_types: list[IndicatorType],
) -> Callable[[type[TIPSource]], type[TIPSource]]:
    def decorator(cls: type[TIPSource]) -> type[TIPSource]:
        if not all(
            isinstance(indicator_type, IndicatorType)
            for indicator_type in indicator_types
        ):
            raise InvalidIndicatorTypeError

        processor_registry.register(indicator_types, cls)

        return cls

    return decorator
