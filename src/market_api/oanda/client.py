import requests
import pandas as pd
from pprint import pprint
from dateutil import parser
from market_api.timeframe import Timeframe
from market_api.granularity import Granularity
from market_api.instrument_meta import InstrumentMeta
from market_api.instrument_data import InstrumentData
import datetime as dt
from typing import List, Dict, Tuple, Iterator
from dask import dataframe as dd
import os
import pytz


class Client:

    OANDA_URL: str = 'https://api-fxpractice.oanda.com/v3'
    DATE_FORMAT: str = '%Y-%m-%dT%H:%M:%S'

    account_id: str
    api_key: str
    cache_candles: int = 4000
    refresh_incomplete: bool = True
    timezone_market = 'Etc/GMT+4'

    def __init__(self, account_id: str, api_key: str):
        self.account_id = account_id
        self.api_key = api_key

    def candles(
        self, symbol: str, granularity: Granularity, price: str,
        time_from: dt.datetime, time_to: dt.datetime, params: dict = {},
    ) -> Timeframe:
        url = f'{self.OANDA_URL}/instruments/{symbol}/candles'

        params['granularity'] = granularity.value
        params['price'] = price

        periods = granularity.range_periods(
            self.cache_candles, time_from, time_to
        )

        parquets = []

        for period_start, period_end in periods:
            parquet_name, directory, full_path = self._parquet_candle(
                symbol, granularity, price, period_start, self.cache_candles,
            )

            parquets.append(full_path)
            os.makedirs(directory, exist_ok=True)

            current_time_market = dt.datetime.now(pytz.timezone(self.timezone_market))
            incomplete = True if current_time_market <= period_end else False
            period_end_corrected = current_time_market if incomplete else period_end

            if (not os.path.isfile(full_path)) or (self.refresh_incomplete and incomplete):
                print(f'downloading parquet {parquet_name}')

                params['from'] = period_start.strftime(self.DATE_FORMAT)
                params['to'] = period_end_corrected.strftime(self.DATE_FORMAT)

                session = requests.Session()
                session.headers.update(self._get_headers())

                response = session.get(url, params=params, data=None, headers=None)
                raw_data = response.json()

                if 'candles' not in raw_data:
                    pprint(raw_data)
                    raise ValueError('Invalid response')
                
                processed_data = []

                for raw_candle in raw_data['candles']:
                    candle = {
                        'time': parser.parse(raw_candle['time']),
                        'volume': int(raw_candle['volume']),
                        'complete': bool(raw_candle['complete']),
                    }

                    for price in ['mid', 'bid', 'ask']:
                        for oh in ['o', 'h', 'l', 'c']:
                            candle[f'{price}_{oh}'] = float(raw_candle[price][oh])

                    processed_data.append(candle)
                
                dataframe = pd.DataFrame(processed_data)
                dataframe.to_parquet(full_path)

        dataframes = []
        for parquet in parquets:
            ddf = dd.read_parquet(parquet)
            if len(ddf) > 0:
                dataframes.append(ddf)

        ddf = dd.concat(dataframes)
        ddf = ddf[ddf.time >= time_from][ddf.time <= time_to]

        return Timeframe(symbol, granularity, ddf)
    
    def instrument_meta(self, symbol: List[str]) -> Iterator[InstrumentMeta]:
        url = f'{self.OANDA_URL}/accounts/{self.account_id}/instruments'
        params = {'instruments': ','.join(symbol)}

        session = requests.Session()
        session.headers.update(self._get_headers())

        response = session.get(url, params=params, data=None, headers=None)
        raw_data = response.json()
        
        for raw_instrument in raw_data['instruments']:
            yield InstrumentMeta.from_oanda(raw_instrument)

    def instrument_data(
        self, symbols: List[str], granularities: List[Granularity],
        time_from: dt.datetime, time_to: dt.datetime,
    ) -> Iterator[InstrumentData]:
        for instrument_meta in self.instrument_meta(symbols):
            instrument_data = InstrumentData(instrument_meta)
            for granularity in granularities:
                instrument_data.add_timeframe(
                    self.candles(
                        instrument_meta.name, granularity, 'MBA', time_from, time_to,
                    )
                )
            
            yield instrument_data

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    @staticmethod           
    def _parquet_candle(
        symbol: str, granularity: Granularity, price: str,
        period_start: dt.datetime, period_length: int
    ) -> Tuple[str, str, str]:
        directory = f'../data/{symbol}/{granularity}/{period_length}'

        if granularity < Granularity.H1:
            directory = f'{directory}/{period_start.year}'

            if granularity < Granularity.M1:
                directory = f'{directory}/{period_start.month}'

        parquet_name = f'{symbol}_{granularity}_{period_length}_{period_start}'
        parquet_name = parquet_name \
            .replace('.', '-') \
            .replace(' ', '-') \
            .replace(':', '-') \
            .lower() \
            
        full_path = f'{directory}/{parquet_name}.parquet'

        return parquet_name, directory, full_path
    