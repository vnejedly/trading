from typing import Dict, Any, List, Iterator
from market_api.granularity import Granularity
from market_api.timeframe import Timeframe
from market_api.currency import Currency
import pandas as pd


class InstrumentMeta:

    name: str
    ins_type: str
    display_name: str
    display_presicion: int
    pip_location: int
    pip_size: float
    trade_units_precision: int
    margin_rate: float

    _data: Dict

    def __init__(
        self, 
        name: str, 
        ins_type: str,
        display_name: str,
        display_precision: int,
        pip_location: int, 
        trade_units_precision: int, 
        margin_rate: float
    ):
        self.name = name
        self.ins_type = ins_type
        self.display_name = display_name
        self.display_presicion = display_precision
        self.pip_location = int(pip_location)
        self.pip_size = 10 ** int(pip_location)
        self.trade_units_precision = int(trade_units_precision)
        self.margin_rate = float(margin_rate)

    def __repr__(self):
        return str(vars(self))
    
    @property
    def base_currency(self) -> Currency:
        return self.currencies[1]
    
    @property
    def currencies(self) -> List[Currency]:
        return [Currency[c] for c in self.name.split('_')]
    
    def round(self, value: float) -> float:
        return round(value, self.display_presicion)
    
    def format(self, value: float) -> str:
        return f'{self.round(value):.{self.display_presicion}f}'
    
    @staticmethod
    def from_oanda(oanda_instrument: Dict) -> 'InstrumentMeta':
        instance = InstrumentMeta(
            oanda_instrument['name'],
            oanda_instrument['type'],
            oanda_instrument['displayName'],
            oanda_instrument['displayPrecision'],
            oanda_instrument['pipLocation'],
            oanda_instrument['tradeUnitsPrecision'],
            oanda_instrument['marginRate'],
        )
    
        instance._data = oanda_instrument
        return instance
    
        
