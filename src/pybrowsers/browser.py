# browser.py

from __future__ import annotations

import sys
import typing

from . import helpers
from .menu import Executor
from .menu import get_menu

if typing.TYPE_CHECKING:
    from pyselector import Menu

    from .datatypes import BrowserSettings
    from .datatypes import ProfilesData

log = helpers.get_logger(__name__)


class BrowsersFound:
    def __init__(self, menu: str) -> None:
        self._menu = menu

    @property
    def menu(self) -> Menu:
        return get_menu(self._menu)

    def choose_browser(self) -> str:
        items = helpers.browsers_found()
        selected, _ = self.menu.prompt(items, prompt="browsers >")
        return selected


class Browser:
    def __init__(self, settings: BrowserSettings, menu: str) -> None:
        self.settings = settings
        self._menu = menu
        self._profiles: ProfilesData = {}
        self.exe = Executor()

    @property
    def name(self) -> str:
        return self.settings.command

    @property
    def bin(self) -> str:
        return self.settings.bin

    @property
    def menu(self) -> Menu:
        return get_menu(self._menu)

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
        profile_selected, _ = self.show_profiles(profiles)
        self.open_profile(profile_selected)

    def show_profiles(self, items: list[str]) -> tuple[str, int]:
        return self.menu.prompt(items=items, case_sensitive=False, prompt=f"{self.name} >")

    def incognito(self) -> None:
        log.debug("Open '%s' in Incognito mode.", self.name)
        self.exe.run(self.bin, self.settings.incognito)

    def open_profile(self, profile: str) -> None:
        if profile == "Incognito":
            self.incognito()
            sys.exit(0)

        if profile not in self.profiles:
            log.error("profile '%s' not found.", profile)
            raise ValueError(f"profile '{profile}' not found.")
        log.debug("opening profile: '%s'", profile)
        command = self.settings.profile_command.format(profile=profile)
        self.exe.run(self.bin, command)

    def _read_settings(self) -> ProfilesData:
        log.debug("Reading settings file: %s", self.settings.path)
        return self.settings.type.read(self.settings.path)
