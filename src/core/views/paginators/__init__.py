from .classic import Paginator
from .lazy import LazyPaginator

__all__: tuple[str, ...] = (
    "Paginator",
    "LazyPaginator",
)
