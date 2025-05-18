from enum import Enum
from market_api.instrument_meta import InstrumentMeta


class Lot(Enum):

    STANDARD: float = 100000
    MINI: float = 10000
    MICRO: float = 1000

    def margin(self, instrument_meta: InstrumentMeta, count: int = 1) -> float:
        currency = instrument_meta.base_currency
        return currency.round(
            int(count) * self.value * instrument_meta.margin_rate
        )
    