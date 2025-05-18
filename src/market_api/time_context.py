from typing import Iterator, Dict, Any
from dask import dataframe as dd
import datetime as dt
from simulator.exceptions import TickDataError, TickCurrentCandleError
from market_api.granularity import Granularity
from market_api.row_set import RowSet
from market_api.row import Row
import pandas as pd


class TimeContext:

    symbol: str
    granularity: Granularity
    time: dt.datetime
    history: dd.DataFrame

    _current: Row
    _latest: Row
    
    def __init__(
        self, symbol: str, granularity: Granularity, 
        ddf: dd.DataFrame, time: dt.datetime
    ):
        self.symbol = symbol
        self.granularity = granularity
        self.time = time
        self.history = ddf.loc[:time]

        self._current = None
        self._latest = None

    @property
    def current(self) -> Row:
        if self._current is None:
            try:
                self._current = Row(self.time, self.history.loc[self.time].to_dict())
            except KeyError:
                raise TickCurrentCandleError(self.symbol, self.granularity)

        return self._current

    @property
    def latest(self) -> Row:
        if self._latest is None:
            try:
                row_data = self.history.iloc[-1]
                candle_time = row_data.name
                
                self._latest = Row(
                    candle_time, row_data.to_dict(),
                    candle_time != self.time
                )
            except IndexError:
                raise TickDataError(self.symbol, self.granularity)

        return self._latest

    def latest_df(self, n: int) -> dd.DataFrame:
        return self.history.loc[self._time_latest_n(n):]
    
    def latest_set(self, n: int) -> RowSet:
        return RowSet(self.latest_df(n))
    
    def _time_latest_n(self, n: int):
        return self.time - n * self.granularity.time_delta
    