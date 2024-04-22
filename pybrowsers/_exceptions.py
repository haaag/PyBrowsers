from __future__ import annotations


class InvalidJSONError(Exception):
    pass


class NoURLError(Exception):
    pass


class NoBrowserRunningError(Exception):
    pass


class NoBrowserFoundError(Exception):
    pass


EXCEPTIONS = (
    InvalidJSONError,
    NoURLError,
    NoBrowserRunningError,
    NoBrowserFoundError,
)
