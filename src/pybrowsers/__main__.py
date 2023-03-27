# main.py

import argparse
import logging
from typing import Sequence

from . import helpers
from .browser import Browser
from .browser import BrowsersFound

log = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser("Simple script that launches browser with the selected profile.")
    parser.add_argument("-b", "--browser", help="Browser to launch (default: firefox)", default="firefox")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-r", "--rofi", help="Use Rofi (default: dmenu)", action="store_true")
    parser.add_argument("-a", "--found", help="Select from browsers found in your system.", action="store_true")

    args = parser.parse_args(argv)

    helpers.logging_debug(args.verbose)
    log.debug("arguments: %s", vars(args))

    name = BrowsersFound(rofi=args.rofi).choose_browser() if args.found else args.browser
    config = helpers.get_browser_config(name)
    browser = Browser(settings=config, rofi=args.rofi)
    browser.load_profiles()
    browser.add_profile("Incognito")
    browser.select_profile()


if __name__ == "__main__":
    main()
