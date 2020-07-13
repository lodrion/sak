import json
import logging
from typing import Callable, Mapping, List, Optional

import funcy
from redis import StrictRedis

from .store import K, V, ReadWriteStore


DEFAULT_KEY_CHUNK_SIZE = 30


class RedisStore(ReadWriteStore[K, V]):
    """Redis-based read write store"""

    def __init__(
        self,
        redis: StrictRedis,
        name: str,
        expiration_seconds: int,
        key_encoder: Optional[Callable[[K], bytes]] = None,
        value_encoder: Optional[Callable[[V], bytes]] = None,
        value_decoder: Optional[Callable[[bytes], V]] = None,
        key_chunk_size: int = DEFAULT_KEY_CHUNK_SIZE,
    ) -> None:
        """Init. By default keys and values are encoded/decoded by json"""
        self._redis = redis
        self._name = name
        self._expiration_seconds = expiration_seconds
        self._key_encoder = lambda x: (
            (name + '/').encode('utf8') +
            (key_encoder(x) if key_encoder else json.dumps(x).encode('utf8'))
        )
        self._value_encoder = value_encoder or json.dumps
        self._value_decoder = value_decoder or json.loads
        self._key_chunk_size = key_chunk_size


    def mget(self, keys: List[K]) -> List[Optional[V]]:
        """Get values for keys"""
        results = []
        for key_chunk in funcy.chunks(self._key_chunk_size, keys):
            encoded_keys = [self._key_encoder(key) for key in key_chunk]
            results.extend(
                self._value_decoder(encoded_data) if encoded_data is not None else None
                for encoded_data in self._redis.mget(encoded_keys)
            )
        return results

    def mset(self, kvs: Mapping[K, V]) -> List[bool]:
        """Get values for keys"""
        with self._redis.pipeline(transaction=False) as pipeline:
            for key, value in kvs.items():
                pipeline.setex(
                    self._key_encoder(key),
                    self._expiration_seconds,
                    self._value_encoder(value)
                )
            return pipeline.execute()


    def delete(self, keys: List[K]) -> List[bool]:
        """Remove list of keys from the store"""
        for encoded_key_chunk in funcy.chunks(
            self._key_chunk_size, (self._key_encoder(key) for key in keys)
        ):
            self._redis.delete(*encoded_key_chunk)

    def clear(self) -> bool:
        """Clear the whole store"""
        keys = self._redis.scan_iter(self._name + "/*")
        for key_chunk in funcy.chunks(self._key_chunk_size, keys):
            self._redis.delete(*key_chunk)
