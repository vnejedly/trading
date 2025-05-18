from typing import Dict
from market_api.instrument_meta import InstrumentMeta
from market_api.timeframe import Timeframe
import datetime as dt


class InstrumentData:

    instrument_meta: InstrumentMeta
    timeframes: Dict[str, Timeframe]

    timeframe_main: Timeframe
    time_from: dt.datetime
    time_to: dt.datetime

    def __init__(self, instrument_meta: InstrumentMeta):
        self.instrument_meta = instrument_meta
        self.timeframes = {}

        self.timeframe_main = None
        self.time_from = None
        self.time_to = None

    def add_timeframe(self, timeframe: Timeframe):
        self.timeframes[timeframe.granularity] = timeframe
        
        if self.timeframe_main is None or (
            timeframe.granularity < self.timeframe_main.granularity
        ):
            self.timeframe_main = timeframe
        
        if (self.time_from is None) or (timeframe.start > self.time_from):
            self.time_from = timeframe.start

        if (self.time_to is None) or (timeframe.end < self.time_to):
            self.time_to = timeframe.end
