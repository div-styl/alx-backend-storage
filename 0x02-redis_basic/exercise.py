#!/usr/bin/env python3
"""Radis module
"""
import uuid
import redis
from functools import wraps
from typing import Any, Callable, Union


def count_calls(method: Callable) -> Callable:
    """Tracks the number of calls"""

    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """Invokes the given method"""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return invoker


def call_history(method: Callable) -> Callable:
    """Tracks the call details for caching purposes"""

    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """Returns outputs ."""
        input_key = "{}:inputs".format(method.__qualname__)
        out_key = "{}:outputs".format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output

    return invoker


def replay(fn: Callable) -> None:
    """Displays the call history"""
    if fn is None or not hasattr(fn, "__self__"):
        return
    redis_store = getattr(fn.__self__, "_redis", None)
    if not isinstance(redis_store, redis.Redis):
        return
    fn_name = fn.__qualname__
    input_key = "{}:inputs".format(fn_name)
    out_key = "{}:outputs".format(fn_name)
    fxn_call_count = 0
    if redis_store.exists(fn_name) != 0:
        fxn_call_count = int(redis_store.get(fn_name))
    print("{} was called {} times:".format(fn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(input_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print(
            "{}(*{}) -> {}".format(
                fn_name,
                fxn_input.decode("utf-8"),
                fxn_output,
            )
        )


class Cache:
    """Represents an object for storing radis in db."""

    def __init__(self) -> None:
        """init the Cache instance."""
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Stores a value in a Redis."""
        data_key = str(uuid.uuid4())
        self._redis.set(data_key, data)
        return data_key

    def get(
        self,
        key: str,
        fn: Callable = None,
    ) -> Union[str, bytes, int, float]:
        """Retrieves a value from radis."""
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        """return radis in storage."""
        return self.get(key, lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """return the radis in storage."""
        return self.get(key, lambda x: int(x))