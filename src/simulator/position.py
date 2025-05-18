from enum import Enum
from typing import Optional, List, Callable
from market_api.candle import Candle
from market_api.currency import Currency
from market_api.instrument_meta import InstrumentMeta
from simulator.exceptions import PositionAlreadyClosedError
from simulator.instrument_context import InstrumentContext
from simulator.context import Context
from simulator.direction import Direction
from simulator.lot import Lot
import datetime as dt
import uuid


class Position:

    class CloseType(Enum):
        MARGIN = 'margin'
        TAKE_PROFIT = 'take_profit'
        STOP_LOSS = 'stop_loss'
        USER = 'user'

    id: uuid.UUID
    instrument: InstrumentMeta
    base_currency: Currency
    
    lot: Lot
    couunt: int
    amount: int
    margin: float

    direction: Direction
    
    price_open: Candle
    price_close: Candle

    take_profit: Optional[float]
    stop_loss: Optional[float]

    handlers: List[Callable]

    time_open: dt.datetime
    time_close: Optional[dt.datetime]

    close_type: Optional[CloseType]
    running: bool
    
    def __init__(
        self, instrument: InstrumentContext, 
        lot: Lot, count: int, direction: Direction,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
    ):
        self.id = uuid.uuid4()
        self.instrument = instrument.instrument_meta
        self.base_currency = instrument.instrument_meta.base_currency
        
        self.lot = lot
        self.count = count
        self.amount = count * lot.value

        self.margin = lot.margin(
            instrument.instrument_meta, count
        )

        self.take_profit = take_profit
        self.stop_loss = stop_loss

        self.handlers = []
        self.direction = direction

        self.time_open = instrument.time
        self.time_close = None

        self.close_type = None
        self.running = True

        self._freeze_price_open(instrument)
        self._freeze_price_close(instrument)

    def unit_profit(self, close_type: Optional[CloseType] = None) -> float:
        if close_type is None:
            close_type = self.close_type
        
        if close_type is None:
            close_type = self.CloseType.USER

        match (close_type, self.direction):
            case (self.CloseType.USER, _):
                close_decisive = self.price_close.close
            case (self.CloseType.MARGIN, Direction.LONG):
                close_decisive = self.price_close.low
            case (self.CloseType.MARGIN, Direction.SHORT):
                close_decisive = self.price_close.high
            case (self.CloseType.STOP_LOSS, Direction.LONG):
                close_decisive = self.price_close.low
            case (self.CloseType.STOP_LOSS, Direction.SHORT):
                close_decisive = self.price_close.high
            case (self.CloseType.TAKE_PROFIT, Direction.LONG):
                close_decisive = self.price_close.high
            case (self.CloseType.TAKE_PROFIT, Direction.SHORT):
                close_decisive = self.price_close.low
            case _:
                raise ValueError(f'Unexpected close type: {close_type.value}')

        unit_profit = self.direction.value * (
            close_decisive - self.price_open.mean
        )

        return self.instrument.round(unit_profit)
    
    def profit(self, close_type: Optional[CloseType] = None) -> float:
        return self.base_currency.round(self.unit_profit(close_type) * self.amount)
    
    def payback(self, close_type: Optional[CloseType] = None) -> float:
        return self.base_currency.round(self.margin + self.profit(close_type))
    
    def margin_convert(self, currency: Currency) -> float:
        price_currency = self.instrument.base_currency.convert(self.margin, currency)
        return currency.round(price_currency)

    def profit_convert(self, currency: Currency) -> float:
        price_currency = self.instrument.base_currency.convert(self.profit(), currency)
        return currency.round(price_currency)
    
    def payback_convert(self, currency: Currency) -> float:
        price_currency = self.instrument.base_currency.convert(self.payback(), currency)
        return currency.round(price_currency)
    
    def add_handler(self, handler: Callable):
        self.handlers.append(handler)
    
    def refresh(self, context: Context) -> bool:
        if not self.running:
            raise PositionAlreadyClosedError(self.id)
        
        self._freeze_price_close(context.get_instrument(self.instrument.name))

        for handler in self.handlers:
            handler(self, context)

        if self.profit(self.CloseType.MARGIN) <= -self.margin:
            self._close_internal(self.CloseType.MARGIN, context)
        elif (
            (self.stop_loss is not None) and 
            (self.unit_profit(self.CloseType.STOP_LOSS) <= -self.stop_loss)
        ):
            self._close_internal(self.CloseType.STOP_LOSS, context)
        elif (
            (self.take_profit is not None) and 
            (self.unit_profit(self.CloseType.TAKE_PROFIT) >= self.take_profit)
        ): 
            self._close_internal(self.CloseType.TAKE_PROFIT, context)
        
        return self.running
    
    def close(self, context: Context):
        if not self.running:
            raise PositionAlreadyClosedError(self.id)

        self._freeze_price_close(context.get_instrument(self.instrument.name))
        self._close_internal(self.CloseType.USER, context)

    def _close_internal(self, close_type: CloseType, context: Context):
        self.time_close = context.time
        self.close_type = close_type
        self.running = False

    def _freeze_price_open(self, instrument: InstrumentContext) -> float:
        match self.direction:
            case Direction.LONG:
                self.price_open = instrument.price.ask
            case Direction.SHORT:
                self.price_open = instrument.price.bid
            case _:
                raise ValueError(f'Unexpected direction: {self.direction.value}')
    
    def _freeze_price_close(self, instrument: InstrumentContext) -> float:
        match self.direction:
            case Direction.LONG:
                self.price_close = instrument.price.bid
            case Direction.SHORT:
                self.price_close = instrument.price.ask
            case _:
                raise ValueError(f'Unexpected direction: {self.direction.value}')
    