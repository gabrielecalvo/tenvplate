import sys
import time
from collections.abc import Collection, Generator
from typing import Any


def progressbar(
    collection: Collection, prefix: str = "", size: int = 60, out: Any = sys.stdout
) -> Generator[Any, Any, None]:
    count = len(collection)
    start = time.time()

    def show(j: float) -> None:
        x = int(size * j / count)
        remaining = ((time.time() - start) / j) * (count - j)
        mins, sec = divmod(remaining, 60)  # limited to minutes
        time_str = f"{int(mins):02}:{sec:04.1f}"
        print(
            f"{prefix}[{'█' * x}{('.' * (size - x))}] {j}/{count} Est wait {time_str}", end="\r", file=out, flush=True
        )

    show(0.1)  # avoid div/0
    for i, item in enumerate(collection):
        yield item
        show(i + 1)
    print("\n", flush=True, file=out)
