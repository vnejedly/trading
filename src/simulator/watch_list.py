from typing import Any, Dict, List


class WatchList:

    variables: Dict[str, Any]

    def __init__(self):
        self.variables = {}

    def add(self, name: str, value: Any):
        self.variables[name] = value

    def get_data(self) -> List[Dict[str, Any]]:
        return [
            {'name': name, 'value': value} 
            for (name, value) in self.variables.items()
        ]
    