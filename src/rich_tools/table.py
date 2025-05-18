import random
import time

from typing import List

from rich.live import Live
from rich.table import Table
from src.rich_tools.rich_tools import ListStatic, Column, ColumnComputed

def generate_list() -> ListStatic:
    my_list = ListStatic()

    my_list.add_column(Column('id', 'ID'))
    my_list.add_column(Column('value', 'Value', lambda value: f"[blue]{value:3.2f}", {'width': 30}))
    my_list.add_column(ColumnComputed('Status', lambda item: "[red]ERROR" if item['value'] < 50 else "[green]SUCCESS"))
        
    my_list.add_argument('show_header', False)
    my_list.add_argument('width', 80)
    
    my_list.min_rows = 10
    my_list.max_rows = 12

    return my_list


def generate_data() -> List:
    data = []
    for row in range(random.randint(2, 6)):
        value = random.random() * 100
        data.append({'id': row, 'value': value})

    return data


list_1 = generate_list()
list_2 = generate_list()

list_3 = generate_list()

list_3.add_argument('width', 160)
list_3.add_argument('show_header', True)

with Live(refresh_per_second=4) as live:
    for _ in range(40):
        time.sleep(0.4)

        super_grid = Table.grid()
        super_grid.add_column()

        grid = Table.grid()
        grid.add_column()
        grid.add_column()
        grid.add_row(list_1.render(generate_data()), list_2.render(generate_data()))

        super_grid.add_row(grid)
        super_grid.add_row(list_3.render(generate_data()))

        live.update(super_grid)
