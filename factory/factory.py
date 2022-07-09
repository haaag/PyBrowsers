from dataclasses import dataclass

from browsers.browser import Browser, ChromiumBrowser, GeckoBrowser
from browsers.menu import DmenuMenu, Menu, RofiMenu
from configuration.configuration import BrowserConfig


@dataclass
class BrowserFactory:
    name: str
    rofi: bool = False
    notification: bool = False

    @property
    def menu(self) -> Menu:
        if self.rofi:
            return RofiMenu()
        else:
            return DmenuMenu()

    @property
    def config(self) -> BrowserConfig:
        return BrowserConfig(self.name, self.menu, self.notification)

    @property
    def browser(self) -> Browser:
        if self.config.type == "ini":
            return GeckoBrowser(self.config, self.config.menu)
        return ChromiumBrowser(self.config, self.config.menu)
