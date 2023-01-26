# main.py

import argparse
from typing import Sequence

from . import helpers
from .browser import Browser
from .browser import BrowsersFound


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser("Simple script that launches browser with the selected profile.")
    parser.add_argument("-b", "--browser", help="Browser to launch (default: firefox)", default="firefox")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-r", "--rofi", help="Use Rofi (default: dmenu)", action="store_true")
    parser.add_argument("-a", "--all", help="Select from browsers found in your system.", action="store_true")

    args = parser.parse_args(argv)

    helpers.set_logging_level(args.verbose)

    if args.verbose:
        print("Arguments:", end=" ")
        __import__("pprint").pprint(vars(args))

    if args.all:
        name = BrowsersFound(rofi=args.rofi).choose_browser()
    else:
        name = args.browser

    config = helpers.get_browser_config(name)
    browser = Browser(settings=config, rofi=args.rofi)
    browser.load_profiles()
    browser.add_profile("Incognito")
    browser.select_profile()


if __name__ == "__main__":
    main()
