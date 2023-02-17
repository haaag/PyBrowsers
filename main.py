# main.py

import argparse
from typing import Sequence

from src.browser_profiles import helpers
from src.browser_profiles.browser import Browser
from src.browser_profiles.browser import BrowsersFound


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser("Simple script that launches browser with the selected profile.")
    parser.add_argument("-b", "--browser", help="Browser to launch (default: firefox)", default="firefox")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-r", "--rofi", help="Use Rofi (default: dmenu)", action="store_true")
    parser.add_argument("-f", "--found", help="Select from browsers found in your system.", action="store_true")
    parser.add_argument("-t", "--test", help="test", action="store_true")

    args = parser.parse_args(argv)

    helpers.set_logging_level(args.verbose)

    if args.verbose:
        print("Arguments:", end=" ")
        __import__("pprint").pprint(vars(args))

    if args.found:
        name = BrowsersFound(rofi=args.rofi).choose_browser()
    else:
        name = args.browser

    settings = helpers.get_browser_config(name)
    browser = Browser(settings=settings, rofi=args.rofi)
    browser.load_profiles()
    browser.add_profile("Incognito")
    browser.select_profile()


if __name__ == "__main__":
    main()
