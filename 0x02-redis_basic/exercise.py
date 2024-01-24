#!/usr/bin/env python3
"""
model for using redis NoSQL
"""
import redis
import uuid
from functools import wraps
from typing import Any, Union, Callable


def count_calls(method: Callable) -> Callable:
    """
    count number of calls
    """

    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """
        wrapper
        """
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return invoker


def call_history(method: Callable) -> Callable:
    """
    store history
    """

    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """
        wrapper
        """
        in_key = "{}:inputs".format(method.__qualname__)
        out_key = "{}:outputs".format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        outputs = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, str(outputs))
        return outputs

    return invoker


def replay(fn: Callable) -> None:
    """
    reply
    """
    if fn is None or not hasattr(fn, "__str__"):
        return
    redit_store = getattr(fn.__self__, "_redis", None)
    if not isinstance(redit_store, redis.Redis):
        return
    fn_name = fn.__qualname__
    in_key = "{}:inputs".format(fn_name)
    out_key = "{}:outputs".format(fn_name)
    fn_call_cnt = 0
    if redit_store.exists(fn_name) != 0:
        fn_call_cnt = int(redit_store.get(fn_name))
    print("{} was called {} times:".format(fn_name, fn_call_cnt))
    inputs = redit_store.lrange(in_key, 0, -1)
    outputs = redit_store.lrange(out_key, 0, -1)
    for fn_inputs, fn_output in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(
            fn_name,
            fn_inputs.decode("utf-8"),
              fn_output))


class Cache:
    """
    model for using redis NoSQL
    """

    def __init__(self):
        """
        init
        """
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    def get(
            self, key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """
        get
        """
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        """
        get_str
        """
        return self.get(key, lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """
        get_int
        """
        return self.get(key, lambda x: int(x))
