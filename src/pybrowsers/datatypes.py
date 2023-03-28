# datatypes.py

from __future__ import annotations

import json
import logging
import shutil
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Mapping
from typing import MutableMapping
from typing import Protocol

log = logging.getLogger(__name__)

BrowserCollection = Mapping[str, dict[str, Any]]

ProfilesData = MutableMapping[str, str]


class ExecutableNotFoundError(Exception):
    pass


class BrowserProfileNotFoundError(Exception):
    pass


class BrowserNotSupportedError(Exception):
    pass


class BrowserSettingsType(Protocol):
    @staticmethod
    def read(file: Path) -> ProfilesData:
        ...

    @staticmethod
    def name() -> str:
        ...


class INI:
    @staticmethod
    def read(file: Path) -> ProfilesData:
        if not file.exists():
            log.error("profile path '%s' not found.", file)
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
            log.error("profile path '%s' not found.", file)
            raise BrowserProfileNotFoundError(f"profile path '{file}' not found.")

        top_level_key = "profile"
        low_level_key = "info_cache"
        profiles = {}

        with Path.open(file, encoding="utf-8", mode="r") as f:
            json_dump = json.load(f)
            profiles_dict = json_dump.get(top_level_key).get(low_level_key)

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
            log.critical("command '%s' not found", self.command)
            raise ExecutableNotFoundError(f"command '{self.command}' not found.")

    @property
    def bin(self) -> str:
        return shutil.which(self.command)

    @property
    def path(self) -> Path:
        return Path(self.profile_file).expanduser()
