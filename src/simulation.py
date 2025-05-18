from simulator.simulator import Simulator
from simulator.account import Account
from simulator.a_controller import AController
from simulator.exceptions import TickCurrentCandleError
from simulator.context import Context
from simulator.account import Account
from simulator.direction import Direction
from simulator.position import Position
from simulator.watch_list import WatchList
from simulator.lot import Lot
from market_api.currency import Currency
from market_api.granularity import Granularity
import datetime as dt
from dotenv import load_dotenv
import os


class SimulationController(AController):

    def tick(
        self, step: int, context: Context, 
        account: Account, watch_list: WatchList
    ) -> str:
        if account.count_running < 20:
            account.position_open(
                'EUR_USD', Lot.MICRO, 1, Direction.SHORT,
                take_profit=0.0050, stop_loss=0.0050,
            )

        watch_list.add('equity', account.equity)


load_dotenv("../.env")

play_account = Account(50000, Currency.USD)

simulator = Simulator(
    play_account, os.environ.get("OANDA_ID"), 
    os.environ.get("OANDA_API_KEY"),
)

simulator.refresh_per_second = 10

simulator.add_controller(SimulationController())

simulator.run_simulation(
    ['EUR_USD'], [Granularity.M1], Granularity.M1,
    dt.datetime(2024, 4, 1, 9, 5, tzinfo=dt.timezone.utc), 
    dt.datetime(2024, 5, 1, 16, 45, tzinfo=dt.timezone.utc),
)
