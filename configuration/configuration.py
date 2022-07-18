import json
import os
from configparser import ConfigParser

from browsers.menu import Menu

config_path = os.path.dirname(os.path.abspath(__file__))
CONFIGFILE = f"{config_path}/config.json"


class ConfigManager:
    def __init__(self, config_name: str, menu: Menu) -> None:
        self.config_name = config_name
        self.menu = menu
        self.config: dict[str, str] = {}
        self.profiles: dict[str, str] = {}

        self._load_config()
        self._process_config_file()

    def _load_config(self) -> None:
        """Reads config.json file."""
        with open(CONFIGFILE) as f:
            data = json.load(f)
            config_list = data["browsers"]

        for browser_config in config_list:
            browser_name = browser_config["name"]
            if browser_name == self.config_name:
                self.config = browser_config

    def _process_config_file(self) -> None:
        if self.type == "ini":
            self._process_ini_file()
        else:
            self._process_json_file()

    def _process_json_file(self) -> None:
        """Process Chromium-type Browser profile file."""

        TOP_LEVEL_KEY = "profile"
        SUB_LEVEL_KEY = "info_cache"

        if not os.path.isfile(self.profiles_file):
            print(f"Profile's file '{self.profiles_file}' not found.")
            self.menu.error(f"'{self.name}' not found. ({self.profiles_file})")

        with open(self.profiles_file) as f:
            json_file = json.load(f)
            profiles_list = json_file.get(TOP_LEVEL_KEY).get(SUB_LEVEL_KEY)

            for profile_path, profile_data in profiles_list.items():
                name = profile_data.get("name")
                self.profiles[name] = profile_path

    def _process_ini_file(self) -> None:
        """Process Gecko-type Browser profile file."""

        if not os.path.isfile(self.profiles_file):
            print(f"Profile's file '{self.profiles_file}' not found.")
            self.menu.error(f"'{self.name}' not found. ({self.profiles_file})")

        profiles_file = ConfigParser()
        profiles_file.read(self.profiles_file)

        for section in profiles_file.sections():
            if "Profile" in section:
                name = profiles_file.get(section, "Name")
                self.profiles[name] = name

    @property
    def type(self) -> str:
        return self.config["type"]

    @property
    def command(self) -> str:
        return self.config["command"]

    @property
    def name(self) -> str:
        return self.config["name"]

    @property
    def profiles_file(self) -> str:
        file = os.path.expanduser(self.config["profile_file"])
        return file

    def __str__(self) -> str:
        return f"{type(self).__name__}(browser={self.name},command={self.command},file={self.profiles_file})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(browser={self.name},command={self.command},file={self.profiles_file})"
