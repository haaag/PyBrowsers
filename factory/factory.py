from dataclasses import dataclass
from typing import Type

from browsers.browser import Browser, ChromiumBrowser, GeckoBrowser
from browsers.menu import DmenuMenu, Menu, RofiMenu
from configuration.configuration import BrowserConfig

BROWSERS: dict[str, Type[GeckoBrowser | ChromiumBrowser]] = {
    "ini": GeckoBrowser,
    "json": ChromiumBrowser,
}


@dataclass
class BrowserFactory:
    name: str
    rofi: bool = False
    notification: bool = False

    @property
    def menu(self) -> Menu:
        if self.rofi:
            return RofiMenu()
        return DmenuMenu()

    @property
    def config(self) -> BrowserConfig:
        return BrowserConfig(self.name, self.menu, self.notification)

    @property
    def browser(self) -> Browser:
        return BROWSERS[self.config.type](self.config, self.config.menu)
