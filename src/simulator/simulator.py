from typing import List, Dict, Any
from market_api.granularity import Granularity
from market_api.oanda.client import Client
from simulator.loop import Loop
from rich_tools.rich_tools import ListStatic, Column, ColumnComputed
from market_api.instrument_meta import InstrumentMeta
from simulator.position import Position
from simulator.a_controller import AController
from simulator.account import Account
from simulator.watch_list import WatchList
from rich.live import Live
from rich.table import Table
import datetime as dt
import warnings


class Simulator:

    refresh_per_second: int = 4
    debug: bool = False

    def __init__(
        self, play_account: Account, 
        oanda_account_id: str, oanda_api_key: str, 
        debug: bool = False,
    ):
        self.market_api = Client(oanda_account_id, oanda_api_key)
        self.loop = Loop(play_account)
        self.debug = debug

        warnings.filterwarnings(
            "ignore", message=
            "Boolean Series key will be reindexed to match DataFrame index."
        )

    def add_controller(self, controller: AController):
        self.loop.add_controller(controller)

    def run_simulation(
        self, symbols: List[str], granularities: List[Granularity],
        time_step: Granularity, time_from: dt.datetime, time_to: dt.datetime,
    ):
        instrument_data = self.market_api.instrument_data(
            symbols, granularities, time_from, time_to
        )

        for instrument in instrument_data:
            self.loop.add_instrument(instrument)

        running_positions = self._running_positions_list()
        globals_list = self._globals_list()
        output_buffer = self._output_buffer()

        with Live(refresh_per_second=self.refresh_per_second) as live:
            def after_tick(
                account: Account, watch_list: WatchList, 
                output: List[Dict[str, Any]]
            ):
                super_grid = Table.grid()
                super_grid.add_column()

                grid = Table.grid()
                
                grid.add_column()
                grid.add_column()

                grid.add_row(
                    running_positions.render(account.positions_running), 
                    globals_list.render(watch_list.get_data()),
                )

                super_grid.add_row(grid)

                if (len(output) > 0):
                    super_grid.add_row(output_buffer.render(output))

                if self.debug:
                    input()

                live.update(super_grid)

            self.loop.run(time_step, time_from, time_to, after_tick)

    @staticmethod
    def _time_format(time: dt.datetime) -> str:
        return time.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def _running_positions_list(cls) -> ListStatic:
        def price_open(item: Position) -> float:
            return item.instrument.format(item.price_open.mean)
        
        def unit_profit(item: Position) -> str:
            value = item.unit_profit()
            color = "green" if value > 0 else "red"
            return f'[{color}]{item.instrument.format(value)}'
        
        def display_name(item: InstrumentMeta) -> str:
            return item.display_name

        my_list = ListStatic()

        my_list.add_column(Column('id', 'id'))
        my_list.add_column(Column('instrument', 'symbol', display_name))
        my_list.add_column(Column('time_open', 'time open', cls._time_format))
        my_list.add_column(ColumnComputed('price open', price_open, args={'justify': 'right'}))
        my_list.add_column(Column('direction', 'direction'))
        my_list.add_column(ColumnComputed('unit profit', unit_profit, args={'justify': 'right'}))
            
        my_list.add_argument('width', 120)
        
        my_list.min_rows = 20
        my_list.max_rows = 20

        return my_list
    
    @staticmethod
    def _globals_list() -> ListStatic:
        my_list = ListStatic()

        my_list.add_column(Column('name', 'name', args={'justify': 'right'}))
        my_list.add_column(Column('value', 'value'))
            
        my_list.add_argument('show_header', False)
        my_list.add_argument('width', 80)
        
        my_list.min_rows = 22
        my_list.max_rows = 22

        return my_list
    
    @classmethod
    def _output_buffer(cls) -> ListStatic:
        my_list = ListStatic()

        my_list.add_column(Column('step', 'step'))
        my_list.add_column(Column('time', 'time', cls._time_format))
        my_list.add_column(Column('result', 'result'))
            
        my_list.add_argument('width', 200)
        
        my_list.min_rows = 10
        my_list.max_rows = 10

        return my_list
    