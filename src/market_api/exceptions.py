import datetime as dt
from market_api.granularity import Granularity


class ConversionRateNotFoundError(Exception):
    
    def __init__(self, from_currency: str, to_currency: str):
        super().__init__(f'No conversion rate found for {from_currency} to {to_currency}')
        