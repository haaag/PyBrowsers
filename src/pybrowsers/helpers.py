# helpers.py

from __future__ import annotations

import logging
import shutil

from .database import BROWSERS
from .datatypes import BrowserNotSupportedError
from .datatypes import BrowserSettings
from .logger import handler

log = logging.getLogger(__name__)


def logging_debug(verbose: bool = False) -> None:
    """Sets the logging level."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(name)s - %(message)s",
        handlers=[handler],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_browser_config(name: str) -> BrowserSettings:
    name = name.lower()
    if name not in BROWSERS:
        log.critical("browser '%s' not supported", name)
        raise BrowserNotSupportedError(f"browser '{name}' not supported.")
    log.debug("selected browser '%s'", name)
    return BrowserSettings(**BROWSERS[name])


def browsers_found() -> list[str]:
    # return [browser for browser in BROWSERS if shutil.which(browser)]
    browsers: list[str] = []
    for browser in BROWSERS:
        found = shutil.which(browser)
        if found:
            log.debug("browser executable '%s' found.", found)
            browsers.append(browser)
    return browsers
