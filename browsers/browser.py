import shlex
import shutil
import subprocess
from typing import Optional, Protocol

from configuration.configuration import BrowserConfig

from .menu import Menu


class BrowserExecutableNotFoundError(Exception):
    def __init__(self, name: str):
        self.message = f"Executable for '{name}' browser not found."
        super().__init__(self.message)


class BrowserProfileNotFoundError(Exception):
    def __init__(self, selected: str):
        self.message = f"Profile: '{selected}' not found."
        super().__init__(self.message)


class Browser(Protocol):
    config: BrowserConfig
    menu: Menu
    profiles: dict[str, str]
    bin: Optional[str]

    def _load_profiles(self) -> None:
        raise NotImplementedError()

    def show_menu(self) -> None:
        raise NotImplementedError()

    def launch_profile(self, profile: str) -> None:
        raise NotImplementedError()

    def notification(self, message: str) -> None:
        raise NotImplementedError()


class GeckoBrowser:
    def __init__(self, config: BrowserConfig, menu: Menu) -> None:
        self.config = config
        self.menu = menu
        self.name: str = self.config.name
        self.command: str = self.config.command
        self.profiles: dict[str, str] = {}
        self.bin = shutil.which(self.name)

        self._load_profiles()

    def _load_profiles(self) -> None:
        self.profiles = self.config.profiles

    def show_menu(self) -> None:
        items = sorted(self.profiles.keys())
        selected = self.menu.show_items(items)

        if selected not in self.profiles and selected is not None:
            self.notification(f"Profile: '{selected}' not found.")
            raise BrowserProfileNotFoundError(selected)

        if selected:
            self.launch_profile(selected)

    def launch_profile(self, profile: str) -> None:
        if not self.bin:
            raise BrowserExecutableNotFoundError(self.name)

        self.notification(f"Launching Profile: {profile}")

        command_str = self.command.format(executable=self.bin, profile=profile)
        subprocess.Popen(
            shlex.split(command_str),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def notification(self, message: str) -> None:
        if not self.config.notification:
            return

        notification_str = (
            f"notify-send '{self.name.capitalize()} profiles script' '{message}'"
        )
        notification = shlex.split(notification_str)
        subprocess.Popen(
            notification, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )


class ChromiumBrowser:
    def __init__(self, config: BrowserConfig, menu: Menu) -> None:
        self.config = config
        self.menu = menu
        self.name: str = self.config.name
        self.command = self.config.command
        self.profiles: dict[str, str] = {}
        self.bin = shutil.which(self.name)

        self._load_profiles()

    def _load_profiles(self) -> None:
        self.profiles = self.config.profiles

    def show_menu(self) -> None:
        items = sorted(self.profiles.keys())
        selected = self.menu.show_items(items)

        if selected not in self.profiles and selected is not None:
            self.notification(f"Profile: {selected} not found.")
            raise BrowserProfileNotFoundError(selected)

        if selected:
            self.launch_profile(self.profiles[selected])

    def launch_profile(self, profile: str) -> None:
        if not self.bin:
            raise BrowserExecutableNotFoundError(self.name)

        profile_name = self.get_profile_name(profile)
        self.notification(f"Launching Profile: {profile_name}")

        command_str = self.command.format(executable=self.bin, profile=profile)
        subprocess.Popen(
            shlex.split(command_str),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def notification(self, message: str) -> None:
        if not self.config.notification:
            return

        notification_str = (
            f"notify-send '{self.name.capitalize()} profiles script' '{message}'"
        )
        notification = shlex.split(notification_str)
        subprocess.Popen(
            notification, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    def get_profile_name(self, profile_target: str) -> str | None:
        for name, profile_dir in self.profiles.items():
            if profile_dir == profile_target:
                return name
        return None
