from typing import Protocol

from configuration.configuration import ConfigManager
from configuration.executor import Executor

from browsers.menu import Menu


class BrowserProfileNotFoundError(Exception):
    def __init__(self, selected: str):
        self.message = f"Profile: '{selected}' not found."
        super().__init__(self.message)


class Browser(Protocol):
    config: ConfigManager
    menu: Menu
    profiles: dict[str, str]
    executor: Executor

    def _load_profiles(self) -> None:
        raise NotImplementedError()

    def show_menu(self) -> None:
        raise NotImplementedError()

    def launch_profile(self, profile: str) -> None:
        raise NotImplementedError()


class GeckoBrowser:
    def __init__(self, config: ConfigManager, menu: Menu, executor: Executor) -> None:
        self.config = config
        self.menu = menu
        self.executor = executor
        self.name: str = self.config.name
        self.command: str = self.config.command
        self.profiles: dict[str, str] = {}

        self._load_profiles()

    def _load_profiles(self) -> None:
        self.profiles = self.config.profiles

    def show_menu(self) -> None:
        items = sorted(self.profiles.keys())
        selected = self.menu.show_items(items)

        if selected not in self.profiles and selected is not None:
            self.executor.send_notification(f"Profile: '{selected}' not found.")
            raise BrowserProfileNotFoundError(selected)

        if selected:
            self.launch_profile(selected)

    def launch_profile(self, profile: str) -> None:
        command = self.command.format(executable=self.executor.bin, profile=profile)
        self.executor.run(command)
        self.executor.send_notification(f"Launching Profile: {profile}")


class ChromiumBrowser:
    def __init__(self, config: ConfigManager, menu: Menu, executor: Executor) -> None:
        self.config = config
        self.menu = menu
        self.executor = executor
        self.name: str = self.config.name
        self.command: str = self.config.command
        self.profiles: dict[str, str] = {}

        self._load_profiles()

    def _load_profiles(self) -> None:
        self.profiles = self.config.profiles

    def show_menu(self) -> None:
        items = sorted(self.profiles.keys())
        selected = self.menu.show_items(items)

        if selected not in self.profiles and selected is not None:
            self.executor.send_notification(f"Profile: {selected} not found.")
            raise BrowserProfileNotFoundError(selected)

        if selected:
            self.launch_profile(self.profiles[selected])

    def launch_profile(self, profile: str) -> None:
        profile_name = self.get_profile_name(profile)
        self.executor.send_notification(f"Launching Profile: {profile_name}")

        command_str = self.command.format(executable=self.executor.bin, profile=profile)
        self.executor.run(command_str)

    def get_profile_name(self, profile_target: str) -> str | None:
        for name, profile_dir in self.profiles.items():
            if profile_dir == profile_target:
                return name
        return None
