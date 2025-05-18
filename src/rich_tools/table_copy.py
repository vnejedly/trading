import random
import time

from rich.live import Live
from rich.table import Table
from rich.panel import Panel

from rich import print
from rich.layout import Layout

layout = Layout()
layout.split_row(
    Layout(name="left"),
    Layout(name="right"),
)

def generate_table() -> Table:
    """Make a new table."""
    table = Table(expand=True, style="blue")
    table.add_column("ID")
    table.add_column("Value")
    table.add_column("Status")

    for row in range(random.randint(2, 6)):
        value = random.random() * 100
        table.add_row(
            f"{row}", f"{value:3.2f}", "[red]ERROR" if value < 50 else "[green]SUCCESS"
        )

    return table

with Live(layout, refresh_per_second=10):
    while True:
        layout["left"].update(generate_table())
        layout["right"].update(generate_table())
        time.sleep(0.1)



# with Live(generate_table(), refresh_per_second=4) as live:
#     for _ in range(40):
#         time.sleep(0.4)
#         live.update(generate_table())