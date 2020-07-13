"""A very simple implementation of a read only store and composition

This is a riff on https://github.com/twitter/storehaus
"""
import abc
from typing import Callable, Generic, List, Mapping, Optional, TypeVar


K = TypeVar('K')
V = TypeVar('V')


class ReadStore(abc.ABC, Generic[K, V]):
    """Store that supports mget"""

    @abc.abstractmethod
    def mget(self, keys: List[K]) -> List[Optional[V]]:
        """Get values for keys"""
        raise NotImplementedError('mget must be reimplemented in concrete implementation')

    def get(self, key: K) -> Optional[V]:
        """Get a single key"""
        return mget([key])[0]


class WriteStore(abc.ABC, Generic[K, V]):
    """Store that supports writing"""

    @abc.abstractmethod
    def mset(self, kvs: Mapping[K, V]) -> List[bool]:
        """Get values for keys"""
        raise NotImplementedError('mset must be reimplemented in concrete implementation')


    @abc.abstractmethod
    def delete(self, keys: List[K]) -> List[bool]:
        """Remove list of keys from the store"""
        raise NotImplementedError('delete must be reimplemented in concrete implementation')


    @abc.abstractmethod
    def clear(self) -> bool:
        """Clear the whole store"""
        raise NotImplementedError('clear must be reimplemented in concrete implementation')


class ReadWriteStore(ReadStore[K, V], WriteStore[K, V]):
    """Store that supports reading and writing"""


class SingleLayerCache(ReadStore[K, V]):
    """A read store that implements a single layer of caching on top of read and readwrite stores"""

    def __init__(self, base: ReadStore[K, V], layer: WriteStore[K, V]) -> None:
        """Initialize"""
        self._base = base
        self._layer = layer

    def mget(self, keys: List[K]) -> List[Optional[V]]:
        """Get a bunch of keys either from the cache layer or from the base"""
        # Note an explicit check for None, because falsy values can be valid keys
        valid_index_and_key_list = [(idx, key) for idx, key in enumerate(keys) if key is not None]
        # Initialize the results
        results = [None] * len(keys)

        if valid_index_and_key_list:
            # Split indices and keys into separate lists
            valid_keys = [ik[1] for ik in valid_index_and_key_list]
            # Keep track of which indices were not hit in the cache
            missed_index_and_key_list = []
            layer_hits = self._layer.mget(valid_keys)
            for layer_hit, index_and_key in zip(layer_hits, valid_index_and_key_list):
                if layer_hit is None:
                    missed_index_and_key_list.append(index_and_key)
                else:
                    results[index_and_key[0]] = layer_hit

            if missed_index_and_key_list:
                missed_keys = [ik[1] for ik in missed_index_and_key_list]
                base_hits = self._base.mget(missed_keys)

                mapping_to_write = {}
                for base_hit, index_and_key in zip(base_hits, missed_index_and_key_list):
                    if base_hit:
                        results[index_and_key[0]] = base_hit
                        mapping_to_write[index_and_key[1]] = base_hit

                self._layer.mset(mapping_to_write)

        return results


class FunctionSingleReadStore(ReadStore[K, V]):
    """Read store that wraps a function that turns key into value"""

    def __init__(self, func: Callable[[K], Optional[V]]) -> None:
        """Init"""
        self._func = func

    def get(self, key: K)-> Optional[V]:
        """Get value for the key"""
        return self._func(key)

    def mget(self, keys: List[K]) -> List[Optional[V]]:
        """Get multiple values"""
        return [self.get(k) for k in keys]
