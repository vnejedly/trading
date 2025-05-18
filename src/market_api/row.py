from typing import Dict, Any
from market_api.candle import Candle
import datetime as dt


class Row:

    time: dt.datetime
    data: Dict[str, Any]

    volume: int
    complete: bool
    delayed: bool

    ask: Candle
    bid: Candle
    mid: Candle

    def __init__(self, time: dt.datetime, data: Dict[str, Any], delayed: bool = False):
        self.time = time
        self.data = data

        self.volume = data['volume']
        self.complete = data['complete']
        self.delayed = delayed

        self.ask = Candle(
            data['ask_o'], data['ask_c'], 
            data['ask_h'], data['ask_l']
        )

        self.bid = Candle(
            data['bid_o'], data['bid_c'], 
            data['bid_h'], data['bid_l']
        )

        self.mid = Candle(
            data['mid_o'], data['mid_c'], 
            data['mid_h'], data['mid_l']
        )
        
    def field(self, field: str) -> Any:
        if field not in self.data:
            raise ValueError(f'Field {field} not found')
        
        return self.data[field]
    