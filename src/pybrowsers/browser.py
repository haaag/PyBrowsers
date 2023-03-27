# browser.py

from __future__ import annotations

import sys
import typing

from . import helpers
from .menu import Dmenu
from .menu import Menu
from .menu import Rofi

if typing.TYPE_CHECKING:
    from .datatypes import BrowserSettings
    from .datatypes import ProfilesData

log = helpers.get_logger(__name__)


def get_menu(rofi: bool = False) -> Menu:
    if rofi:
        return Rofi()
    return Dmenu()


class BrowsersFound:
    def __init__(self, rofi: bool = False) -> None:
        self.rofi = rofi

    @property
    def menu(self) -> Menu:
        return get_menu(self.rofi)

    def choose_browser(self) -> str:
        items = helpers.browsers_found()
        return self.menu.show(items, prompt="browsers >")


class Browser:
    def __init__(self, settings: BrowserSettings, rofi: bool = False) -> None:
        self.settings = settings
        self.rofi = rofi
        self._profiles: ProfilesData = {}

    @property
    def name(self) -> str:
        return self.settings.command

    @property
    def bin(self) -> str:
        return self.settings.bin

    @property
    def menu(self) -> Menu:
        return get_menu(self.rofi)

    @property
    def profiles(self) -> ProfilesData:
        return self._profiles

    @profiles.setter
    def profiles(self, profiles: ProfilesData) -> None:
        self._profiles = profiles

    def load_profiles(self) -> None:
        profiles = self._read_settings()
        log.debug("Set profiles: %s", profiles)
        self.profiles = profiles

    def add_profile(self, new_profile: str) -> None:
        log.debug("Adding profile: '%s'", new_profile)
        self._profiles[new_profile] = new_profile

    def select_profile(self) -> None:
        profiles = list(self.profiles.values())
        profile_selected = self.show_profiles(profiles)
        self.open_profile(profile_selected)

    def show_profiles(self, items: list[str]) -> str:
        return self.menu.show(items=items, prompt=f"{self.name} >")

    def incognito(self) -> None:
        log.debug("Open '%s' in Incognito mode.", self.name)
        self.menu.executor.run(self.bin, self.settings.incognito)

    def open_profile(self, profile: str) -> None:
        if profile == "Incognito":
            self.incognito()
            sys.exit(0)

        if profile not in self.profiles:
            log.error("profile '%s' not found.", profile)
            raise ValueError(f"profile '{profile}' not found.")
        log.debug("opening profile: '%s'", profile)
        command = self.settings.profile_command.format(profile=profile)
        self.menu.executor.run(self.bin, command)

    def _read_settings(self) -> ProfilesData:
        log.debug("Reading settings file: %s", self.settings.path)
        return self.settings.type.read(self.settings.path)
