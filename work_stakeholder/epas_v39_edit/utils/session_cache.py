"""Bounded per-Streamlit-session read cache.

The cache is session-local so authenticated data never crosses users. A small
LRU cap prevents long-lived sessions from accumulating unbounded objects.
"""
from __future__ import annotations
import time
from collections import OrderedDict
from typing import Any, Callable
import hashlib
import json
import streamlit as st

DEFAULT_TTL = 8.0
MAX_ENTRIES = 128
CACHE_VERSION = "v34"

def _state() -> OrderedDict:
    raw = st.session_state.get("epas_read_cache_v32")
    if raw is None:
        raw = OrderedDict()
        st.session_state["epas_read_cache_v32"] = raw
    return raw

def make_key(namespace: str, *parts: Any, **params: Any) -> str:
    """Stable, collision-resistant cache key factory shared by all read paths."""
    payload = {
        "v": CACHE_VERSION,
        "namespace": namespace,
        "parts": [str(x) for x in parts],
        "params": {k: params[k] for k in sorted(params)},
    }
    raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"{namespace}:{digest}"


def get(key: str) -> Any | None:
    cache = _state()
    item = cache.get(key)
    if item is None:
        return None
    expires_at, value = item
    if expires_at < time.monotonic():
        cache.pop(key, None)
        return None
    cache.move_to_end(key)
    return value

def put(key: str, value: Any, ttl_seconds: float = DEFAULT_TTL) -> Any:
    cache = _state()
    cache[key] = (time.monotonic() + max(0.5, float(ttl_seconds)), value)
    cache.move_to_end(key)
    while len(cache) > MAX_ENTRIES:
        cache.popitem(last=False)
    return value

def cached_call(key: str, fn: Callable[[], Any], ttl_seconds: float = DEFAULT_TTL) -> Any:
    hit = get(key)
    if hit is not None:
        return hit
    return put(key, fn(), ttl_seconds)

def clear_prefixes(prefixes: list[str]) -> None:
    cache = _state()
    if not prefixes:
        return
    prefixes = tuple(prefixes)
    for key in list(cache.keys()):
        if key.startswith(prefixes):
            cache.pop(key, None)

def clear() -> None:
    st.session_state.pop("epas_read_cache_v32", None)
    # Clean up the previous v3.1 cache if a session persisted across release upgrades.
    st.session_state.pop("epas_read_cache_v31", None)
