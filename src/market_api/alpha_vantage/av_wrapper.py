import requests
from typing import List, Dict


class BaseQuery:

    function: str
    params: Dict[str, str]

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.params = {}

    @property
    def url(self) -> str:
        return self._func_url + self._query_string
    
    @property
    def data(self) -> Dict:
        r = requests.get(self.url)
        return r.json()

    @property
    def _query_string(self) -> str:
        prefix = '&' if len(self.params) > 0 else ''
        return prefix + '&'.join([
            f'{key}={value}' for key, value in self.params.items()
        ])

    @property
    def _func_url(self) -> str:
        return f'{self.base_url}?apikey={self.api_key}&function={self.function}'
    
    def _set_param(self, key: str, value: str) -> None:
        self.params[key] = value


class NewsSentiment(BaseQuery):
        
    function = 'NEWS_SENTIMENT'
    ticker_list: List[str]

    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url, api_key)
        self.ticker_list = []

    def add_ticker(self, ticker: str) -> 'NewsSentiment':
        self.ticker_list.append(ticker)
        self._set_param('tickers', self._tickers)
        return self
    
    def set_time_from(self, time_from: str) -> 'NewsSentiment':
        self._set_param('time_from', time_from)
        return self
    
    def set_time_to(self, time_to: str) -> 'NewsSentiment':
        self._set_param('time_to', time_to)
        return self
    
    def set_limit(self, limit: int) -> 'NewsSentiment':
        self._set_param('limit', str(limit))
        return self
        
    def sort_earliest(self) -> 'NewsSentiment':
        return self.set_sort('EARLIEST')
        
    def sort_latest(self) -> 'NewsSentiment':
        return self.set_sort('LATEST')
    
    def set_sort(self, sort: str) -> 'NewsSentiment':
        self._set_param('sort', sort)
        return self
        
    @property
    def _tickers(self) -> str:
        return ','.join(self.ticker_list)
        
        
class AlphaVantageWrapper:

    base_url: str = 'https://www.alphavantage.co/query'
    api_key: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    def news_sentiment(self) -> NewsSentiment:
        return NewsSentiment(self.base_url, self.api_key)
    
    