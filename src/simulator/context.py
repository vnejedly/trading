import pandas as pd
from pandas.core.series import Series
from market_api.timeframe import Timeframe
from market_api.instrument_data import InstrumentData
from simulator.instrument_context import InstrumentContext
from typing import Dict
import datetime as dt


class Context:
    
    time: dt.datetime
    instruments: Dict[str, InstrumentContext]

    def __init__(self, time: dt.datetime):
        self.time = time
        self.instruments = {}

    def add_instrument(self, instrument_data: InstrumentData):
        instrument_context = InstrumentContext(
            self.time, instrument_data.instrument_meta
        )

        for timeframe in instrument_data.timeframes.values():
            instrument_context.add_timeframe(timeframe)

        self.instruments[instrument_data.instrument_meta.name] = instrument_context
        
    def get_instrument(self, name: str) -> InstrumentContext:
        if name not in self.instruments.keys():
            raise ValueError(f'Instrument {name} not found')
        
        return self.instruments[name]
    