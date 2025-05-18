import pandas as pd
from abc import ABC
from typing import List
import dask.dataframe as dd


class IndicatorsMixin(ABC):

    data: dd.DataFrame
    traces: List[str]

    def _init_indicators(self):
        self.traces = []
    
    def moving_average(self, column: str, period: int, name: str = None): 
        if name is None:
            name = f'ma_{column}_{period}'

        # def func(ddf: dd.DataFrame, period: int):
        #     return ddf[column].rolling(period).mean()
        
        # self.data[name] = self.data.map_overlap(
        #     func, period=period,
        #     before=100, after=100,
        # )
        self.data[name] = self.data[column].rolling(window=period).mean()
        self.traces.append(name)

    def bollinger_bands(self, price_type: str, period: int, std: float, name: str = None):
        if name is None:
            name = f'bb_{price_type}_{period}'

        def price(phase: str) -> str:
            return f'{price_type}_{phase}'
        
        typical_price = (self.data[price('h')] + self.data[price('l')] + self.data[price('c')]) / 3
        std_dev = typical_price.rolling(window=period).std()
        ma = typical_price.rolling(window=period).mean()

        self.data[f'{name}_ma'] = ma
        self.data[f'{name}_up'] = ma + (std_dev * std)
        self.data[f'{name}_lo'] = ma - (std_dev * std)

        for trace in ['ma', 'up', 'lo']:
            self.traces.append(f'{name}_{trace}')
