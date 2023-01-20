import json
import logging
from configparser import ConfigParser
from pathlib import Path

from browsers.menu import Menu

log = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).resolve().parent
CONFIG_FILE = CONFIG_DIR / "config.json"


class ConfigManager:
    def __init__(self, config_name: str, menu: Menu) -> None:
        self.config_name = config_name
        self.menu = menu
        self.config: dict[str, str] = {}
        self.profiles: dict[str, str] = {}

        self._load_config()
        self._process_config_file()

    def _load_config(self) -> None:
        with open(CONFIG_FILE, encoding="utf-8", mode="r") as file:
            data = json.load(file)
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

        if not CONFIG_FILE.exists():
            self.menu.error(f"'{self.name}' not found. ({self.profiles_file})")

        with open(self.profiles_file, encoding="utf-8", mode="r") as file:
            json_file = json.load(file)
            profiles_list = json_file.get(TOP_LEVEL_KEY).get(SUB_LEVEL_KEY)

            for profile_path, profile_data in profiles_list.items():
                name = profile_data.get("name")
                self.profiles[name] = profile_path

    def _process_ini_file(self) -> None:
        """Process Gecko-type Browser profile file."""

        if not CONFIG_FILE.exists():
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
    def profiles_file(self) -> Path:
        return Path(self.config["profile_file"]).expanduser()

    def __str__(self) -> str:
        return f"{type(self).__name__}(browser={self.name},command={self.command},file={self.profiles_file})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(browser={self.name},command={self.command},file={self.profiles_file})"
