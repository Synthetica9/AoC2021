from time import perf_counter
from rich.console import Console
from contextlib import contextmanager
import sys

console = Console()


@contextmanager
def timer(name):
    before = perf_counter()
    yield
    after = perf_counter()

    took = after - before
    unit = "s"
    if took < 1:
        took *= 1000
        unit = "ms"
    if took < 1:
        took *= 1000
        unit = "μs"

    print(f"[bold red]{name}[/bold red]: took [bold]{took:.02}{unit}[/bold]", file=sys.stderr)
