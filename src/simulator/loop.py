from typing import List, Dict, Optional, Callable
from market_api.instrument_data import InstrumentData
from market_api.granularity import Granularity
from simulator.a_controller import AController
from simulator.context import Context
from simulator.account import Account
from simulator.watch_list import WatchList
import datetime as dt


class Loop:

    account: Account

    instruments: Dict[str, InstrumentData]
    controllers: List[AController]

    time_min: Optional[dt.datetime]
    time_max: Optional[dt.datetime]

    def __init__(self, account: Account):
        self.account = account

        self.instruments = {}
        self.controllers = []

        self.time_min = None
        self.time_max = None

    def add_instrument(self, instrument_data: InstrumentData):
        self.instruments[instrument_data.instrument_meta.name] = instrument_data

        if (self.time_min is None) or (instrument_data.time_from > self.time_min):
            self.time_min = instrument_data.time_from

        if (self.time_max is None) or (instrument_data.time_to < self.time_max):
            self.time_max = instrument_data.time_to

    def add_controller(self, controller: AController):
        self.controllers.append(controller)

    def run(
        self, time_step: Granularity, 
        time_from: dt.datetime, time_to: dt.datetime,
        after_tick: Callable,
    ):
        realtime_start = dt.datetime.now()

        time_range = time_to - time_from
        steps_count = int(time_range / time_step.time_delta)

        for controller in self.controllers:
            controller.steps_count = steps_count

        current_time = time_from
        current_step = 0

        output = []

        while current_time <= time_to:
            currency = self.account.currency.name
            realtime_current = dt.datetime.now()
            duration = realtime_current - realtime_start
            
            watch_list = WatchList()

            watch_list.add('step', current_step)
            watch_list.add('duration', duration)
            watch_list.add('time', self._time_format(current_time))
            watch_list.add('balance', f'{self.account.balance} {currency}')
            watch_list.add('running', self.account.count_running)
            watch_list.add('closed', self.account.count_closed)

            try:
                context = Context(current_time)
                for instrument in self.instruments.values():
                    context.add_instrument(instrument)

                self.account.refresh(context)

                result = 'N/A'
                for controller in self.controllers:
                    result = controller.tick(
                        current_step, context, self.account, watch_list
                    )

            except Exception as exception:
                result = f'[red]{exception.__class__.__name__}: {str(exception)}'
                    
            except KeyboardInterrupt:
                print('Simulation stopped by user')
                break

            if result is not None:
                output.append({
                    'step': current_step,
                    'time': current_time,
                    'result': result
                })

            after_tick(self.account, watch_list, output)

            current_time += time_step.time_delta
            current_step += 1

    @staticmethod
    def _time_format(time: dt.datetime) -> str:
        return time.strftime('%Y-%m-%d %H:%M:%S')
    
    