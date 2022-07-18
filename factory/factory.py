from dataclasses import dataclass
from typing import Type

from browsers.browser import Browser, ChromiumBrowser, GeckoBrowser
from browsers.menu import DmenuMenu, Menu, RofiMenu
from configuration.configuration import ConfigManager
from configuration.executor import Executor

BROWSERS: dict[str, Type[GeckoBrowser | ChromiumBrowser]] = {
    "ini": GeckoBrowser,
    "json": ChromiumBrowser,
}


@dataclass
class BrowserFactory:
    name: str
    executor: Executor
    rofi: bool = False

    @property
    def menu(self) -> Menu:
        if self.rofi:
            return RofiMenu()
        return DmenuMenu()

    @property
    def config(self) -> ConfigManager:
        return ConfigManager(self.name, self.menu)

    @property
    def browser(self) -> Browser:
        return BROWSERS[self.config.type](self.config, self.config.menu, self.executor)
