from abc import ABC, abstractmethod
from simulator.context import Context
from simulator.account import Account
from simulator.watch_list import WatchList


class AController(ABC):

    steps_count: int
    
    @abstractmethod
    def tick(self, step: int, context: Context, account: Account, watch_list: WatchList) -> str:
        pass
