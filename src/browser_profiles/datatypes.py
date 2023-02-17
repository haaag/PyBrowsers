# datatypes.py

import json
import shutil
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Mapping
from typing import MutableMapping
from typing import Protocol

BrowserCollection = Mapping[str, dict[str, Any]]

ProfilesData = MutableMapping[str, str]


class ExecutableNotFound(Exception):
    pass


class BrowserProfileNotFoundError(Exception):
    pass


class BrowserNotSupportedError(Exception):
    pass


class BrowserSettingsType(Protocol):
    @staticmethod
    def read(file: Path) -> ProfilesData:
        ...


class INI:
    @staticmethod
    def read(file: Path) -> ProfilesData:
        if not file.exists():
            raise BrowserProfileNotFoundError(f"profile path '{file}' not found.")

        parser = ConfigParser()
        parser.read(file)
        profiles = {}

        for section in parser.sections():
            if "Profile" in section:
                name = parser.get(section, "Name")
                profiles[name] = name

        return profiles

    @staticmethod
    def name() -> str:
        return "ini"


class JSON:
    @staticmethod
    def read(file: Path) -> ProfilesData:
        if not file.exists():
            raise BrowserProfileNotFoundError(f"profile path '{file}' not found.")

        TOP_LEVEL_KEY = "profile"
        SUB_LEVEL_KEY = "info_cache"
        profiles = {}

        with open(file, encoding="utf-8", mode="r") as f:
            json_dump = json.load(f)
            profiles_dict = json_dump.get(TOP_LEVEL_KEY).get(SUB_LEVEL_KEY)

            for path, data in profiles_dict.items():
                profiles[data.get("name")] = path

        return profiles

    @staticmethod
    def name() -> str:
        return "json"


@dataclass
class BrowserSettings:
    name: str
    command: str
    profile_command: str
    incognito: str
    profile_file: Path
    type: INI | JSON

    def __post_init__(self) -> None:
        if not shutil.which(self.command):
            raise ExecutableNotFound(f"command '{self.command}' not found.")

    @property
    def bin(self) -> str:
        return shutil.which(self.command)  # type: ignore

    @property
    def path(self) -> Path:
        return Path(self.profile_file).expanduser()
