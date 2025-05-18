import datetime as dt


class Candle:

    open: float
    close: float
    high: float
    low: float

    def __init__(
        self,
        open: float, close: float, 
        high: float, low: float
    ):
        self.open = open
        self.close = close
        self.high = high
        self.low = low

    @property
    def direction(self) -> int:
        if self.close == self.open:
            return 0
            
        return 1 if self.close > self.open else -1
    
    @property
    def mean(self) -> float:
        return (self.open + self.low + self.high + self.close) / 4
    
    @property
    def span(self) -> float:
        return self.high - self.low
    
    @property
    def body(self) -> float:
        return abs(self.close - self.open)
    
    @property
    def shadow_up(self) -> float:
        return self.high - max(self.open, self.close)
    
    @property
    def shadow_down(self) -> float:
        return min(self.open, self.close) - self.low
    