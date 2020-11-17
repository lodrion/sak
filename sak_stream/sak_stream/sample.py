from collections import abc
import copy
import random
from typing import Iterable, Iterator, List, TypeVar


T = TypeVar('T')


class BaseSampler(abc.Iterator):
    """Base stream sampler"""
    def __init__(
        self, sample_size: int, underlier: Iterable[T], store_copy: bool
    ) -> None:
        """Setup"""
        self._sample_size = sample_size
        self._store_copy = store_copy
        self._underlier = iter(underlier)
        self._sample: List[T] = []
        super(BaseSampler, self).__init__()

    def __iter__(self) -> Iterator[T]:
        """We are an iterator"""
        return self

    @property
    def sample(self) -> List[T]:
        """Get the count"""
        return self._sample

    def _get_store_value(self, v):
        """Get a value that should be stored"""
        if self._store_copy:
            return copy.deepcopy(v)
        else:
            return v


class HeadSample(BaseSampler):
    """Iterable passthrough that stored first N elements of the underlier"""

    def __init__(
        self, sample_size: int, underlier: Iterable[T], store_copy: bool = False
    ) -> None:
        """Setup"""
        super(HeadSample, self).__init__(sample_size, underlier, store_copy)

    def __next__(self) -> T:
        """Return the next element and store the head element if necessary"""
        v = next(self._underlier)
        if len(self._sample) < self._sample_size:
            self._sample.append(self._get_store_value(v))
        return v


class ReservoirSample(BaseSampler):
    """Iterable passthrough that stored first N elements of the underlier"""

    def __init__(
        self, sample_size: int, underlier: Iterable[T], store_copy: bool = False
    ) -> None:
        """Setup"""
        self._seen = 0
        super(ReservoirSample, self).__init__(sample_size, underlier, store_copy)

    def __next__(self) -> T:
        """Return the next element and store the head element if necessary"""
        v = next(self._underlier)
        self._seen += 1
        if len(self._sample) < self._sample_size:
            self._sample.append(self._get_store_value(v))
        else:
            pos = random.randint(0, self._seen)
            if pos < self._sample_size:
                self._sample[pos] = self._get_store_value(v)

        return v
