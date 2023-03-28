# main.py

from __future__ import annotations

import argparse
import logging
from typing import Sequence

from . import helpers
from .browser import Browser
from .browser import BrowsersFound

log = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser("Simple script that launches browser with the selected profile.")
    parser.add_argument(
        "--menu",
        choices=["rofi", "dmenu", "fzf"],
        help="Select a menu (default: dmenu)",
        default="dmenu",
    )
    parser.add_argument("-b", "--browser", help="Browser to launch (default: firefox)", default="firefox")
    parser.add_argument("-r", "--rofi", help="Use Rofi (default: dmenu)", action="store_true")
    parser.add_argument("-a", "--found", help="Select from browsers found in your system.", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")

    args = parser.parse_args(argv)

    helpers.logging_debug(args.verbose)
    log.debug("arguments: %s", vars(args))

    name = BrowsersFound(menu=args.menu).choose_browser() if args.found else args.browser
    config = helpers.get_browser_config(name)
    browser = Browser(settings=config, menu=args.menu)
    browser.load_profiles()
    browser.add_profile("Incognito")
    browser.select_profile()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
