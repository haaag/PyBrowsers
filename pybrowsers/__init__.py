#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import logging
import os
import shlex
import shutil
import subprocess
import sys
import textwrap
from configparser import ConfigParser
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import NamedTuple

from pyselector import Menu

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

# TODO:
# - [X] Prioritize json files
# - [X] Drop class UserProfile
# - [X] Add color class
# - [X] Output to --json


# FIX:
# - [X] In profiles_read_ini and profiles_read_json, return raw_data
# - [X] In class Browser, create Profiles object

# XDG
DEFAULT_DATA_HOME = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
DEFAULT_APP_HOME = DEFAULT_DATA_HOME / 'pybrowsers'

# Data
BROWSERS: dict[str, Browser] = {}

# App
APP_NAME = 'PyBrowsers'
__version__ = '0.0.8'
APP_HELP = textwrap.dedent(
    f"""    usage: pybrowsers [-l] [-d DISABLE] [-e ENABLE] [-f] [-i INFO] 
                      [-m {{menu}}] [-v] [-V] [browser]

    Simple yet powerful script for managing profiles in multiple web browsers.

    options:
        browser                     Browser name
        -e, --enable                Enable browser
        -d, --disable               Disable browser
        -f, --found                 Browsers found
        -l, --list                  Browser list and status
        -i, --info                  Browser data
        -m, --menu                  Select menu (default: dmenu)
        -V, --version               Show version
        -h, --help                  Show help
        -v, --verbose               Verbose mode

    supported menus:
        {list(Menu.registered().keys())}
    """
)


class C:
    COLORS: ClassVar = {
        'BOLD_RED': '\033[31;1;6m',
        'RED': '\033[31m',
        'BLUE': '\033[34m',
        'YELLOW': '\033[33m',
        'CYAN': '\033[36m',
        'GREEN': '\033[32m',
        'GREY': '\033[90m',
        'RESET': '\033[0m',
    }

    @staticmethod
    def color(color: str, text: str) -> str:
        return f'{C.COLORS.get(color)}{text}{C.COLORS.get("RESET")}'


# Logger Config
FMT = '[{levelname:^7}] {name:<30}: {message} (line:{lineno})'
FORMATS = {
    logging.DEBUG: C.color('GREY', FMT),
    logging.INFO: C.color('CYAN', FMT),
    logging.WARNING: C.color('YELLOW', FMT),
    logging.ERROR: C.color('RED', FMT),
    logging.CRITICAL: C.color('BOLD_RED', FMT),
}


class CustomFormatter(logging.Formatter):
    def format(self, record):  # type: ignore[no-untyped-def]
        log_fmt = FORMATS[record.levelno]
        formatter = logging.Formatter(log_fmt, style='{')
        return formatter.format(record)


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger = logging.getLogger(__name__)


class BrowserProfile(NamedTuple):
    name: str
    key: str
    command: str


def browser_get(name: str) -> Browser:
    try:
        name = name.lower()
        browser = BROWSERS[name]
    except KeyError:
        raise ValueError(f'{name=} not found') from None
    return browser


def browser_all_found(browsers: dict[str, Browser]) -> dict[str, Browser]:
    return {
        b.name: b for b in browsers.values() if shutil.which(b.command) and b.enabled
    }


def browser_select(menu: MenuInterface, browsers: dict[str, Browser]) -> Browser | None:
    selected, _ = menu.prompt(items=tuple(browsers), prompt=f'{APP_NAME}> ')
    if selected is None:
        return None
    return browser_get(selected)


def browser_register(browser: Browser) -> None:
    name = browser.name.lower()
    if name in BROWSERS:
        return
    BROWSERS[name] = browser


def browser_update(browser: Browser) -> None:
    name = browser.name.lower()
    if name not in BROWSERS:
        raise ValueError(f'browser={name} not found.')
    BROWSERS[name] = browser


def browser_save_to_json(browser: Browser) -> None:
    file = DEFAULT_APP_HOME / f'{browser.name.lower()}.json'
    with file.open(mode='w') as f:
        f.write(browser.to_json())
    return


def browser_create(data: dict[str, Any]) -> Browser:
    return Browser(**data)


def browser_disable(name: str) -> None:
    browser = browser_get(name)
    browser.enabled = False
    logger.info(f'browser={browser.name} disabled')
    browser_save_to_json(browser)


def browser_enable(name: str) -> None:
    browser = browser_get(name)
    browser.enabled = True
    logger.info(f'browser={browser.name} enabled')
    browser_save_to_json(browser)


def browsers_status() -> list[str]:
    info = [browser_info(b) for b in BROWSERS.values()]
    return format_title(C.color('GREEN', text='BROWSERS STATUS'), info)


def browser_info(browser: Browser) -> str:
    name = C.color('BLUE', text=browser.name)
    status = '(enabled)'
    if not browser.enabled:
        name = C.color('YELLOW', text=browser.name)
        status = '(disabled)'
    if shutil.which(browser.command) is None:
        name = C.color('RED', text=browser.name)
        status = '(not found)'
    return format_bullet_line(name, status)


def browser_load_from_json() -> None:
    files = DEFAULT_APP_HOME.glob('*.json')
    for file in files:
        data = load_json_file(file)
        browser = browser_create(data)
        browser_update(browser)


def profile_select(menu: MenuInterface, browser: Browser) -> BrowserProfile | None:
    selected, _ = menu.prompt(items=tuple(browser.profiles), prompt=f'{browser.name}> ')
    if selected is None:
        return None
    return browser.get_profile(selected)


def profiles_read_json(filepath: Path) -> list[dict[str, str]]:
    """
    "profile": {
        "info_cache": {
            "Profile 1": {...},
            "Profile 2": {...},
            ...
        }
    }
    """
    assert_file(filepath)
    profiles: list[dict[str, str]] = []
    parent_container_name = 'profile'
    child_container_name = 'info_cache'

    data = load_json_file(filepath)

    try:
        parent_container = data[parent_container_name]
        child_container: dict[str, Any] = parent_container[child_container_name]
    except KeyError as err:
        raise ValueError(err) from err
    for key, profile in child_container.items():
        name = profile.get('name')
        profiles.append({'name': name, 'key': key})
    return profiles


def profiles_read_ini(filepath: Path) -> list[dict[str, str]]:
    assert_file(filepath)
    profiles: list[dict[str, str]] = []

    logger.debug(f"filepath from 'read_ini_profiles'={filepath}")
    parser = load_ini_file(filepath)

    for section in parser.sections():
        if 'Profile' not in section:
            continue
        name = parser.get(section, 'Name')
        profiles.append({'name': name, 'key': name})
    return profiles


def load_json_file(filepath: Path) -> dict[str, Any]:
    try:
        logger.debug(f'Reading file={filepath.name!r}')
        with filepath.open(encoding='utf-8', mode='r') as file:
            data = json.load(file)
    except FileNotFoundError:
        err_msg = f'Json file {filepath.name!r} not found'
        logger.error(err_msg)
        raise FileNotFoundError(err_msg) from None
    return data


def load_ini_file(filepath: Path) -> ConfigParser:
    if not filepath.exists():
        err_msg = f'INI file path {filepath.name!r} not found.'
        logger.error(err_msg)
        raise ValueError(err_msg)

    parser = ConfigParser()
    parser.read(filepath)
    return parser


def assert_file(file: Path) -> None:
    err_msg = f'file={file!s} is not a file.'
    try:
        if file.is_dir():
            logger.error(err_msg)
            raise IsADirectoryError(err_msg)
        if not file.exists():
            err_msg = f'file={file!s} not found'
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)
    except (FileNotFoundError, IsADirectoryError) as err:
        raise err


def execute_command(commands: str) -> int:
    try:
        logger.debug(f'Executing={commands!r}')
        args = shlex.split(commands)

        completed_process = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
        return completed_process.returncode
    except subprocess.SubprocessError as e:
        logging.exception(e)
        raise e


def create_profile_obj(data: dict[str, str]) -> BrowserProfile:
    return BrowserProfile(name=data['name'], key=data['key'], command=data['command'])


@dataclass
class Manager:
    @staticmethod
    def flag_incognito(program: str) -> str:
        raise NotImplementedError

    @staticmethod
    def flag_open(program: str, profile: str) -> str:
        raise NotImplementedError

    @staticmethod
    def data_extractor(browser: Browser) -> list[dict[str, str]]:
        raise NotImplementedError


class BlinkManager(Manager):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def flag_incognito(program: str) -> str:
        return f'{program} --incognito'

    @staticmethod
    def flag_open(program: str, profile: str) -> str:
        return f'{program} --profile-directory={profile!r} --no-default-browser-check'

    @staticmethod
    def data_extractor(browser: Browser) -> list[dict[str, str]]:
        path = Path(browser.path).expanduser()
        return profiles_read_json(path)


class GeckoManager(Manager):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def flag_incognito(program: str) -> str:
        return f'{program} --private-window'

    @staticmethod
    def flag_open(program: str, profile: str) -> str:
        return f'{program} -P {profile!r}'

    @staticmethod
    def data_extractor(browser: Browser) -> list[dict[str, str]]:
        path = Path(browser.path).expanduser()
        return profiles_read_ini(path)


@dataclass
class Browser:
    name: str
    command: str
    path: str
    engine: str
    enabled: bool
    _profiles: dict[str, BrowserProfile] = field(default_factory=dict)

    @property
    def manager(self) -> type[Manager]:
        return ENGINES_TYPES[self.engine]

    @property
    def incognito(self) -> BrowserProfile:
        return BrowserProfile(
            name='Incognito',
            key='Incognito',
            command=self.manager.flag_incognito(self.command),
        )

    def get_profile(self, name: str) -> BrowserProfile:
        return self.profiles[name]

    def add_profile(self, profile: BrowserProfile) -> None:
        if profile.name not in self._profiles:
            self._profiles[profile.name] = profile

    def load_profiles(self) -> None:
        incognito = self.incognito
        profiles = {p.name: p for p in self.process_profiles()}
        profiles[incognito.name] = incognito
        self._profiles = profiles

    def process_profiles(self) -> list[BrowserProfile]:
        result: list[BrowserProfile] = []
        data_extracted = self.manager.data_extractor(self)
        for data in data_extracted:
            data['command'] = self.manager.flag_open(self.command, data['key'])
            profile = create_profile_obj(data)
            result.append(profile)
        return result

    @property
    def profiles(self) -> dict[str, BrowserProfile]:
        if not self._profiles:
            self.load_profiles()
        return self._profiles

    def open(self, profile: BrowserProfile) -> int:
        return execute_command(commands=profile.command)

    def to_json(self) -> str:
        return json.dumps(
            {
                'name': self.name,
                'command': self.command,
                'path': self.path,
                'engine': self.engine,
                'enabled': self.enabled,
            },
            indent=2,
        )


brave = Browser(
    name='Brave',
    command='brave',
    path='~/.config/BraveSoftware/Brave-Browser/Local State',
    engine='blink',
    enabled=True,
)
chromium = Browser(
    name='Chromium',
    command='chromium',
    path='~/.config/chromium/Local State',
    engine='blink',
    enabled=True,
)
firefox = Browser(
    name='Firefox',
    command='firefox',
    path='~/.mozilla/firefox/profiles.ini',
    engine='gecko',
    enabled=True,
)
google_chrome = Browser(
    name='Chrome',
    command='google-chrome',
    path='~/.config/google-chrome/Local State',
    engine='blink',
    enabled=True,
)
librewolf = Browser(
    name='LibreWolf',
    command='librewolf',
    path='~/.librewolf/profiles.ini',
    engine='gecko',
    enabled=True,
)
browser_register(brave)
browser_register(chromium)
browser_register(firefox)
browser_register(google_chrome)
browser_register(librewolf)


ENGINES_TYPES: dict[str, type[Manager]] = {
    'blink': BlinkManager,
    'gecko': GeckoManager,
}


def format_title(title: str, items: list[str]) -> list[str]:
    return [f'\n> {title}\n', *items]


def format_bullet_line(label: str, value: str) -> str:
    return f' - {label: <25} {value}'


def setup_project() -> None:
    if DEFAULT_APP_HOME.exists():
        return
    DEFAULT_APP_HOME.mkdir(exist_ok=True)


def setup_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )
    parser.add_argument('browser', nargs='?')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-d', '--disable')
    parser.add_argument('-e', '--enable')
    parser.add_argument('-f', '--found', action='store_true', default=True)
    parser.add_argument('-i', '--info')
    parser.add_argument('-m', '--menu', default='dmenu')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument('-h', '--help', action='store_true')
    return parser


def args_and_exit(args: argparse.Namespace) -> None:
    if args.help:
        print(APP_HELP)
        sys.exit(0)

    if args.list:
        browser_load_from_json()
        for item in browsers_status():
            print(item)
        print('')
        sys.exit(0)

    if args.version:
        print(APP_NAME, __version__)
        sys.exit(0)

    if args.info:
        browser = browser_get(args.info)
        print(browser.to_json())
        sys.exit(0)

    if args.enable:
        browser_enable(args.enable)
        sys.exit(0)

    if args.disable:
        browser_disable(args.disable)
        sys.exit(0)


def main() -> int:
    parser = setup_args()
    args = parser.parse_args()
    browser_load_from_json()
    args_and_exit(args)

    menu = Menu.get(args.menu)

    if args.verbose:
        level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(level=level, handlers=[handler])

    if args.browser:
        browser = browser_get(args.browser)
    if args.found:
        browsers = browser_all_found(BROWSERS)
    browser = browser_select(menu, browsers) # type: ignore[assignment]

    if browser is None:
        return 1

    profile = profile_select(menu, browser)

    if profile is None:
        return 1

    return browser.open(profile)


if __name__ == '__main__':
    sys.exit(main())
