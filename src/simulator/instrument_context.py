from typing import Dict
from market_api.instrument_meta import InstrumentMeta
from market_api.granularity import Granularity
from market_api.time_context import TimeContext
from market_api.timeframe import Timeframe
from market_api.row import Row
import datetime as dt


class InstrumentContext:

    time: dt.datetime
    instrument_meta: InstrumentMeta

    timeframes: Dict[Granularity, TimeContext]
    timeframe_main: TimeContext

    _price: Row

    def __init__(self, time: dt.datetime, instrument_meta: InstrumentMeta):
        self.time = time
        self.instrument_meta = instrument_meta

        self.timeframes = {}
        self.timeframe_main = None

        self._price = None

    @property
    def price(self) -> Row:
        if self._price is None:
            self._price = self.timeframe_main.latest

        return self._price
    
    @property
    def spread(self) -> float:
        return self.instrument_meta.round(
            self.price.ask.close - self.price.bid.close
        )

    def add_timeframe(self, time_frame: Timeframe):
        time_context = time_frame.get_context(self.time)

        if time_context.symbol != self.instrument_meta.name:
            raise ValueError(
                f'Symbol does not match: '
                f'{time_context.symbol} != {self.instrument_meta.name}'
            )
        
        if self.timeframe_main is None or (
            time_context.granularity < self.timeframe_main.granularity
        ):
            self.timeframe_main = time_context

    def get_timeframe(self, granularity: Granularity) -> TimeContext:
        if granularity not in self.timeframes.keys():
            raise ValueError(f'Timeframe {granularity} not found')
        
        return self.timeframes[granularity]