import datetime as dt
from market_api.granularity import Granularity
import uuid


class TickDataError(Exception):
    
    def __init__(self, symbol: str, granularity: Granularity):
        super().__init__(f'No data available for for tick ({symbol}, {granularity.value})')


class TickCurrentCandleError(Exception):
    
    def __init__(self, symbol: str, granularity: Granularity):
        super().__init__(f'No current candle available for tick ({symbol}, {granularity.value})')


class PositionAlreadyClosedError(Exception):
    
    def __init__(self, position_id: uuid.UUID):
        string_id = str(position_id)
        super().__init__(f'Position {string_id} already closed')


class PositionNotFoudError(Exception):
    
    def __init__(self, position_id: uuid.UUID):
        string_id = str(position_id)
        super().__init__(f'Position {string_id} not found')


class BalanceTooLowError(Exception):
    
    def __init__(self, balance: float, margin: float):
        super().__init__(f'Balance {balance} too low for margin {margin}')
