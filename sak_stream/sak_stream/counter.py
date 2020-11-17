from collections import abc
from typing import Iterable, Iterator, TypeVar


T = TypeVar('T')


class StreamCounter(abc.Iterator):
    """Iterable passthrough that counts the number of consumed elements"""

    def __init__(self, iterable: Iterable[T]) -> None:
        """Setup"""
        self._count = 0
        self._underlier = iter(iterable)
        super(StreamCounter, self).__init__()

    def __iter__(self) -> Iterator[T]:
        """This is an iterator, satisfy the interface"""
        return self

    def __next__(self) -> T:
        """Increment count and return the next element"""
        v = next(self._underlier)
        self._count += 1
        return v

    @property
    def count(self) -> int:
        """Get the count"""
        return self._count
