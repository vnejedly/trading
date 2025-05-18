from abc import ABC, abstractmethod
from rich.table import Table
from typing import Any, List, Dict, Callable, Optional
from rich.console import RenderableType


class IColumn(ABC):

    display_name: str
    callback: Optional[Callable]
    args: Dict[str, Any]
    
    @abstractmethod
    def get_value(self, item: Dict|Any) -> str:
        pass


class Column(IColumn):
    
    key: str
    
    def __init__(
        self, key: str, display_name: str, 
        callback: Optional[Callable] = None,
        args: Dict[str, Any] = {},
    ):
        self.key = key
        self.display_name = display_name
        self.callback = callback
        self.args = args
    
    def get_value(self, item: Dict|Any) -> str:
        if isinstance(item, dict):
            raw_value = item.get(self.key, 'N/A')
        else:
            raw_value = getattr(item, self.key, 'N/A')
            if callable(raw_value):
                raw_value = raw_value()

        return str(
            self.callback(raw_value) 
            if callable(self.callback) 
            else raw_value
        )

    
class ColumnComputed(IColumn):
    
    def __init__(
        self, display_name: str, 
        callback: Callable,
        args: Dict[str, Any] = {},
    ) -> None:
        self.display_name = display_name
        self.callback = callback
        self.args = args
    
    def get_value(self, item: Dict|Any) -> str:
        return str(self.callback(item))
    

class ListStatic():

    columns: List[IColumn]

    min_rows: int = 0
    max_rows: Optional[int] = None
    
    args: Dict[str, Any] = {}

    def __init__(self) -> None:
        self.args = {}
        self.columns = []

    def add_column(self, column: IColumn) -> None:
        self.columns.append(column)

    def add_argument(self, key: str, value: Any) -> None:
        self.args[key] = value

    def render(self, data: List[Any]) -> RenderableType:
        table = Table(**self.args)

        for column in self.columns:
            table.add_column(column.display_name, **column.args)

        items = data[-self.max_rows:] if self.max_rows else data

        for item in items:
            table.add_row(*[column.get_value(item) for column in self.columns])

        for i in range(len(items) + 1, self.min_rows +1):
            table.add_row()

        return table
    