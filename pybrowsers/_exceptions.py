from __future__ import annotations


class InvalidJSONError(Exception): ...


class NoURLError(Exception): ...


class NoBrowserRunningError(Exception): ...


class NoBrowserFoundError(Exception): ...


EXCEPTIONS = (
    InvalidJSONError,
    NoURLError,
    NoBrowserRunningError,
    NoBrowserFoundError,
)
