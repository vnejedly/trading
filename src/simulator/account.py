import datetime as dt
from typing import List, Dict, Optional
from market_api.currency import Currency
from simulator.instrument_context import InstrumentContext
from simulator.position import Position
from simulator.direction import Direction
from simulator.context import Context
from simulator.lot import Lot

from simulator.exceptions import (
    BalanceTooLowError, 
    PositionAlreadyClosedError, 
    PositionNotFoudError,
)


class Account:
    
    _balance: float

    currency: Currency
    contexxt: Optional[Context]

    positions_index: Dict[str, Position]

    positions_running: List[Position]
    positions_closed: List[Position]

    _payback_running: float

    def __init__(self, balance: float, currency: Currency):
        self._balance = balance
        self.currency = currency
        self.context = None

        self.positions_index = {}
        self.positions_running = []
        self.positions_closed = []

        self._payback_running = 0

    @property
    def balance(self) -> float:
        return self.currency.round(self._balance)
    
    @balance.setter
    def balance(self, value: float):
        self._balance = self.currency.round(value)

    @property
    def payback_running(self) -> float:
        return self.currency.round(self._payback_running)
    
    @property
    def equity(self) -> float:
        return self.currency.round(self.balance + self._payback_running)
    
    @property
    def count_running(self) -> int:
        return len(self.positions_running)
    
    @property
    def count_closed(self) -> int:
        return len(self.positions_closed)

    def position_open(
        self, instrument: str, 
        lot: Lot, count: int, direction: Direction,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
    ) -> Position:
        instrument_context = self.context.get_instrument(instrument)

        position = Position(
            instrument_context, lot, count, 
            direction, take_profit, stop_loss
        )

        margin_required = position.margin_convert(self.currency)

        if margin_required > self.balance:
            raise BalanceTooLowError(self.balance, margin_required)
        
        self.balance -= margin_required

        self.positions_index[position.id] = position
        self.positions_running.append(position)

        return position
    
    def position_close(self, position_id: str) -> Position:
        position = self.position_get(position_id)

        if not position.running:
            raise PositionAlreadyClosedError(position.id)

        position.close(self.context)
        self._resolve_closed(position)

        return position

    def position_get(self, position_id: str) -> Position:
        if position_id not in self.positions_index.keys():
            raise PositionNotFoudError(position_id)
        
        return self.positions_index[position_id]
    
    def refresh(self, context: Context):
        self.context = context
        self._payback_running = 0

        for position in self.positions_running:
            position.refresh(context)

            if position.running:
                self._payback_running += position.payback_convert(self.currency)
            else:
                self._resolve_closed(position)

    def _resolve_closed(self, position: Position):
        self.positions_running.remove(position)
        self.positions_closed.append(position)

        self.balance += position.payback_convert(self.currency)
