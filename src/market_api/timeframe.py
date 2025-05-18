import pandas as pd
import datetime as dt
from market_api.granularity import Granularity
from market_api.indicators import IndicatorsMixin
from plotting.candle_plot import CandlePlot
from market_api.time_context import TimeContext
import dask.dataframe as dd
from dask_expr._collection import Scalar
import pytz


class Timeframe(IndicatorsMixin):

    symbol: str
    granularity: Granularity
    data: dd.DataFrame
    start: dt.datetime
    end: dt.datetime

    def __init__(
        self, symbol: str,
        granularity: Granularity, 
        data: dd.DataFrame
    ):
        self._init_indicators()

        self.symbol = symbol
        self.granularity = granularity
        
        self.data = data

        if len(self.data) > 0:
            self.data = self.data.set_index('time', sorted=True)
        
        self.data = self.data.compute()

        self.start = data.time.min().compute()
        self.end = data.time.max().compute()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.granularity} from {self.start} to {self.end}'

    def __hash__(self) -> int:
        return hash((self.granularity, self.start, self.end))
    
    def get_context(self, time: dt.datetime) -> TimeContext:
        return TimeContext(self.symbol, self.granularity, self.data, time)
    
    def get_candle_plot(self, index_from: dt.datetime, index_to: dt.datetime) -> CandlePlot:
        plot = CandlePlot(self.symbol, self.data.loc[index_from:index_to])

        for trace in self.traces:
            plot.add_trace(trace)

        return plot.update_layout(nticks=5)
    