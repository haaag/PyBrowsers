import sys

import click

from configuration.executor import Executor
from factory.factory import BrowserFactory

SUPPORTED_BROWSERS = [
    "firefox",
    "chromium",
    "brave",
    "google-chrome",
    "waterfox-classic",
]


def show(factory: BrowserFactory) -> None:
    print("Name:\t\t", factory.name)
    print("Executable:\t", factory.browser.executor.bin)
    print("ProfileFile:\t", factory.config.profiles_file)


@click.command()
@click.option(
    "--browser-name",
    "-b",
    type=click.Choice(SUPPORTED_BROWSERS),
    help="Browser to launch",
)
@click.option("--all", "-a", is_flag=True, help="Show supported browser and profiles.")
@click.option(
    "--rofi",
    is_flag=True,
    default=False,
    help="Choose profile with Rofi (dmenu Default).",
)
@click.option(
    "--show-config",
    is_flag=True,
    default=False,
    help="Show config's dictonary.",
)
@click.option(
    "--notification", "-n", is_flag=True, default=False, help="Show notifications."
)
def main(
    browser_name: str, rofi: bool, all: bool, show_config: bool, notification: bool
) -> None:
    """
    Simple script that launches browser with the selected profile.
    """
    executor = Executor(browser_name, notification)
    if all:
        factory = BrowserFactory(browser_name, executor, rofi)
        browser_selected = factory.menu.show_items(
            items=SUPPORTED_BROWSERS, prompt="browser > "
        )

        if browser_selected is None:
            sys.exit()

        factory.name = browser_selected
        factory.browser.show_menu()
        sys.exit()

    if not browser_name:
        print("\nUse --help.\nPlease choose a browser.")
        sys.exit(1)

    factory = BrowserFactory(browser_name, executor, rofi)

    if show_config:
        show(factory)
        sys.exit()

    factory.browser.show_menu()


if __name__ == "__main__":
    main()
