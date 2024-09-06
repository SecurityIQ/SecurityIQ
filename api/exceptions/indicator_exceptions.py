from api.typings.models.indicators import IndicatorType


class InvalidIndicatorTypeError(Exception):
    def __init__(self) -> None:
        super().__init__(f"Invalid indicator type. Must be of type {IndicatorType}")
