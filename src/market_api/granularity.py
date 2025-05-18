from enum import Enum
from datetime import timedelta, datetime
from typing import Tuple, Iterator, List
import pytz

TIME_BEGINNING = datetime(1900, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)

GRANULARITY_TIME = {
    'S5': timedelta(seconds=5),
    'S10': timedelta(seconds=10),
    'S15': timedelta(seconds=15),
    'S30': timedelta(seconds=30),
    'M1': timedelta(minutes=1),
    'M2': timedelta(minutes=2),
    'M4': timedelta(minutes=4),
    'M5': timedelta(minutes=5),
    'M10': timedelta(minutes=10),
    'M15': timedelta(minutes=15),
    'M30': timedelta(minutes=30),
    'H1': timedelta(hours=1),
    'H2': timedelta(hours=2),
    'H3': timedelta(hours=3),
    'H4': timedelta(hours=4),
    'H6': timedelta(hours=6),
    'H8': timedelta(hours=8),
    'H12': timedelta(hours=12),
    'D': timedelta(days=1),
    'W': timedelta(weeks=1),
    'M': timedelta(days=30),
}

class Granularity(Enum):

    S5 = 'S5'  # 5 second candlesticks, minute alignment
    S10 = 'S10'  # 10 second candlesticks, minute alignment
    S15 = 'S15'  # 15 second candlesticks, minute alignment
    S30 = 'S30'  # 30 second candlesticks, minute alignment
    M1 = 'M1'  # 1 minute candlesticks, minute alignment
    M2 = 'M2'  # 2 minute candlesticks, hour alignment
    M4 = 'M4'  # 4 minute candlesticks, hour alignment
    M5 = 'M5'  # 5 minute candlesticks, hour alignment
    M10 = 'M10'  # 10 minute candlesticks, hour alignment
    M15 = 'M15'  # 15 minute candlesticks, hour alignment
    M30 = 'M30'  # 30 minute candlesticks, hour alignment
    H1 = 'H1'  # 1 hour candlesticks, hour alignment
    H2 = 'H2'  # 2 hour candlesticks, day alignment
    H3 = 'H3'  # 3 hour candlesticks, day alignment
    H4 = 'H4'  # 4 hour candlesticks, day alignment
    H6 = 'H6'  # 6 hour candlesticks, day alignment
    H8 = 'H8'  # 8 hour candlesticks, day alignment
    H12 = 'H12'  # 12 hour candlesticks, day alignment
    D = 'D'  # 1 day candlesticks, day alignment
    W = 'W'  # 1 week candlesticks, aligned to start of week
    M = 'M'  # 1 month candlesticks, aligned to first day of the month

    def __lt__(self, other: 'Granularity') -> bool:
        return other._value_index > self._value_index

    def __gt__(self, other: 'Granularity') -> bool: 
        return other._value_index < self._value_index
    
    def period_length(self, period_size: int) -> timedelta:
        return period_size * self.time_delta
    
    def range_periods(
        self, period_size: int, 
        start: datetime, end: datetime
    ) -> Iterator[Tuple[datetime, datetime]]:
        if start < TIME_BEGINNING:
            raise ValueError('Start time is before the beginning of time')
        
        if end < start:
            raise ValueError('End time is before start time')

        delta_from_start = start - TIME_BEGINNING
        period_length = self.period_length(period_size)

        periods_from_beginning = int(delta_from_start / period_length)
        start_anchored = TIME_BEGINNING + periods_from_beginning * period_length

        period_start = start_anchored
        while period_start < end:
            period_end = period_start + period_length
            yield period_start, period_end
            period_start += period_length
    
    @property
    def time_delta(self) -> timedelta:
        return GRANULARITY_TIME[self.value]
            
    @property
    def _value_index(self) -> int:
        return list(self.__class__).index(self)
    