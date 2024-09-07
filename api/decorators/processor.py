import logging
from collections.abc import Callable

from api.exceptions.indicator_exceptions import InvalidIndicatorTypeError
from api.processors.indicator.baseclass import TIPSource
from api.registries.processor import processor_registry
from api.typings.models.indicators import IndicatorType

logger = logging.getLogger(__name__)


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
        logger.debug("Registered %s for %s", cls, indicator_types)

        return cls

    return decorator
