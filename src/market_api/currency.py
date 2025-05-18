from typing import Dict
from enum import Enum


EXCHANGE_RATES: Dict[str, float] = {
    'USD': 1.0,  'EUR': 1.2,
    'GBP': 1.4,  'JPY': 0.01,
    'AUD': 0.8,  'CAD': 0.9,
    'CHF': 1.1,  'NZD': 0.7,
    'ZAR': 0.06, 'CNY': 0.15,
    'CZK': 0.05, 'SEK': 0.1,
}


ROUND_DECIMALS: Dict[str, int] = {
    'USD': 2, 'EUR': 2,
    'GBP': 2, 'JPY': 0,
    'AUD': 2, 'CAD': 2,
    'CHF': 2, 'NZD': 2,
    'ZAR': 2, 'CNY': 2,
    'CZK': 0, 'SEK': 2,
}


class Currency(Enum):

    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    JPY = 'JPY'
    AUD = 'AUD'
    CAD = 'CAD'
    CHF = 'CHF'
    NZD = 'NZD'
    ZAR = 'ZAR'
    CNY = 'CNY'
    CZK = 'CZK'
    SEK = 'SEK'

    def __str__(self):
        return self.value
    
    @property
    def exchange_rate(self) -> float:
        return EXCHANGE_RATES[self.value]
    
    def convert(self, value: float, currency_to: 'Currency') -> float:
        return value * self.exchange_rate / currency_to.exchange_rate
    
    def round(self, price: float) -> float:
        return round(price, ROUND_DECIMALS[self.value])
    
    def format(self, price: float) -> str:
        return f'{self.round(price):.{ROUND_DECIMALS[self.value]}f}'
    