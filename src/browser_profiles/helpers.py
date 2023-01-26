# helpers.py

import logging
import shutil

from .database import BROWSERS
from .datatypes import BrowserNotSupportedError
from .datatypes import Settings


def set_logging_level(verbose: bool = False) -> None:
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s]:%(name)s - %(message)s")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_browser_config(name: str) -> Settings:
    if name not in BROWSERS:
        raise BrowserNotSupportedError(f"Browser '{name}' not supported.")
    logging.debug("Selected browser '%s'", name)
    return Settings(**BROWSERS[name])


def browsers_found(log: logging.Logger) -> list[str]:
    # return [browser for browser in BROWSERS if shutil.which(browser)]
    browsers: list[str] = []
    for browser in BROWSERS:
        found = shutil.which(browser)
        if found:
            log.debug("Browser executable '%s' found.", found)
            browsers.append(browser)
    return browsers
