from typing import List, Iterator
from market_api.row import Row
from dask import dataframe as dd


class RowSet:

    data: dd.DataFrame

    def __init__(self, data: dd.DataFrame):
        self.data = data

    @property
    def rows(self) -> Iterator[Row]:
        for index, row in self.data.iterrows():
            yield Row(index, row.to_dict())
