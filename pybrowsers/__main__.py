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
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import NamedTuple
from typing import Self
from typing import Sequence

from pyselector import Menu

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

logger = logging.getLogger(__name__)

__version__ = '0.0.13'
__appname__ = 'PyBrowsers'

ROOT = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
HOME = ROOT / __appname__.lower()
HELP = textwrap.dedent(
    f"""    usage: pybrowsers [-l] [-d DISABLE] [-e ENABLE] [-f] [-t]
                      [-m MENU] [-v] [-V] [browser] [-o URL]

    Simple yet powerful script for managing profiles in multiple web browsers.

    options:
        browser             Browser name
        -e, --enable        Enable browser
        -d, --disable       Disable browser
        -u, --url           Open <URL> in browser
        -l, --list          Show browsers list and status
        -t, --table         Show browsers list with detail
        -m, --menu          Select menu (default: dmenu)
        -f, --found         Browsers found
        -V, --version       Show version
        -h, --help          Show help
        -v, --verbose       Verbose mode

    supported menus:
        {list(Menu.registered().keys())}

    locations:
        {ROOT / 'pybrowsers'}
    """
)

# colors
CYAN = '\033[36m{}\033[0m'
ORANGE = '\033[33m{}\033[0m'
RED = '\033[31m{}\033[0m'
DOT_UNICODE = '\u00b7'


class InvalidJSONError(Exception): ...


class NoURLError(Exception): ...


class NoBrowserFoundError(Exception): ...


EXCEPTIONS = (
    InvalidJSONError,
    NoURLError,
    NoBrowserFoundError,
)


def log_error_and_exit(msg: str) -> None:
    logger.error(f'{__appname__.lower()}:{msg}:')
    sys.exit(1)


def shorten_path_str(filepath: str, length: int, parts: int) -> str:
    """
    Split the path into separate parts, select the last 'length'
    elements and join them again
    """
    if len(filepath) < length:
        return str(filepath)
    short_path = '~/...' / Path(*Path(filepath).parts[-parts:])
    return str(short_path)


def print_table(rows: Sequence[tuple[str, ...]]) -> None:
    """
    Prints out a table using the data in `rows`, which is assumed to be a
    sequence of sequences with the 0th element being the header.
    """
    # https://gist.github.com/lonetwin/4721748

    # figure out column widths
    widths = [len(max(columns, key=len)) for columns in zip(*rows)]

    # print the header
    header, data = rows[0], rows[1:]
    print(' | '.join(format(title, '%ds' % width) for width, title in zip(widths, header)))

    # print the separator
    print('-+-'.join('-' * width for width in widths))

    # print the data
    for row in data:
        print(' | '.join(format(cdata, '%ds' % width) for width, cdata in zip(widths, row)))


def validate_data_from_json(data: dict[str, Any]) -> None:
    json_format_keys = ('name', 'command', 'path', 'engine', 'enabled')
    for key in json_format_keys:
        if key in data:
            continue
        err_msg = f'key {key!r} not found in {data!r}'
        raise InvalidJSONError(err_msg)


class Setup:
    def home(self) -> None:
        if HOME.exists():
            logger.debug(f'directory {HOME.name!r} already exists')
            return

        logger.debug(f'creating directory {HOME.name!r}')
        HOME.mkdir(exist_ok=True)

    def files(self) -> None:
        self.home()

    def menu(self, name: str) -> MenuInterface:
        return Menu.get(name)

    def logging(self, on: bool = False) -> None:
        level = logging.DEBUG if on else logging.ERROR
        logging.basicConfig(level=level)

    def args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter, add_help=False
        )
        parser.add_argument('browser', nargs='?')
        parser.add_argument('-l', '--list', action='store_true')
        parser.add_argument('-d', '--disable', action='store_true')
        parser.add_argument('-e', '--enable', action='store_true')
        parser.add_argument('-f', '--found', action='store_true', default=True)
        parser.add_argument('-u', '--url', nargs='?')
        parser.add_argument('-t', '--table', action='store_true')
        parser.add_argument('-m', '--menu', default='dmenu')
        parser.add_argument('-v', '--verbose', action='store_true')
        parser.add_argument('-V', '--version', action='store_true')
        parser.add_argument('-h', '--help', action='store_true')
        parser.add_argument('--test', action='store_true')

        args = parser.parse_args()
        self.logging(args.verbose)
        logging.debug(vars(args))

        return args


class Files:
    @staticmethod
    def read_json(filepath: Path) -> dict[str, Any]:
        try:
            logger.debug(f'reading file {filepath.name!r}')
            with filepath.open(encoding='utf-8', mode='r') as file:
                data = json.load(file)
        except FileNotFoundError:
            log_error_and_exit(f'JSON file {filepath.name!r} not found')
        except JSONDecodeError:
            log_error_and_exit(f'JSON file {filepath.name!r} is not valid JSON')
        return data

    @staticmethod
    def read_ini(filepath: Path) -> ConfigParser:
        if not filepath.exists():
            log_error_and_exit(f'INI file path {filepath.name!r} not found.')

        parser = ConfigParser()
        parser.read(filepath)
        return parser

    @staticmethod
    def write(path: Path, data: str) -> None:
        with path.open(mode='w', encoding='utf-8') as f:
            f.write(data)

    @staticmethod
    def read(path: Path) -> dict[str, dict[str, str]]:
        with path.open(mode='r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_browser(path: Path, browser: Browser) -> None:
        file = path / f'{browser.name.lower()}.json'
        with file.open(mode='w') as f:
            f.write(browser.to_json())
        return

    @staticmethod
    def assert_exists(file: Path) -> None:
        if not file.exists():
            log_error_and_exit(f"file '{file!s}' is not a file.")
        if file.is_dir():
            log_error_and_exit(f"file '{file!s}' not found")


@dataclass
class Flags:
    cmd: str

    @property
    def incognito(self) -> str:
        raise NotImplementedError

    def launch(self, profile: str) -> str:
        raise NotImplementedError

    @property
    def new_tab(self) -> str:
        raise NotImplementedError

    @property
    def new_window(self) -> str:
        raise NotImplementedError

    @staticmethod
    def data_extractor(path: Path) -> list[dict[str, str]]:
        # FIX: extract method
        raise NotImplementedError


class BlinkFlags(Flags):
    def __init__(self, cmd: str) -> None:
        super().__init__(cmd)

    @property
    def incognito(self) -> str:
        return f'{self.cmd} --incognito'

    def launch(self, profile: str) -> str:
        return f'{self.cmd} --profile-directory={profile!r} --no-default-browser-check'

    @property
    def new_tab(self) -> str:
        return self.cmd

    @property
    def new_window(self) -> str:
        return f'{self.cmd} --new-window'

    @staticmethod
    def data_extractor(path: Path) -> list[dict[str, str]]:
        # FIX: extract method
        return ProfileFileReader.blink(path)


class GeckoFlags(Flags):
    def __init__(self, cmd: str) -> None:
        super().__init__(cmd)

    @property
    def incognito(self) -> str:
        return f'{self.cmd} --private-window'

    def launch(self, profile: str) -> str:
        return f'{self.cmd} -P {profile!r}'

    @property
    def new_tab(self) -> str:
        return f'{self.cmd} -new-tab'

    @property
    def new_window(self) -> str:
        return f'{self.cmd} --new-window'

    @staticmethod
    def data_extractor(path: Path) -> list[dict[str, str]]:
        # FIX: extract method
        return ProfileFileReader.gecko(path)


_TYPES: dict[str, type[Flags]] = {
    'blink': BlinkFlags,
    'gecko': GeckoFlags,
}


class Profile(NamedTuple):
    name: str
    key: str
    cmd: str

    def launch(self) -> int:
        return Process.run(self.cmd)

    def open(self, url: str) -> int:
        return Process.run(f'{self.cmd} {url}')

    def new_tab(self, url: str) -> int:
        return Process.run(f'{self.cmd} -new-tab {url}')


class ProfileFileReader:
    @staticmethod
    def blink(filepath: Path) -> list[dict[str, str]]:
        """
        "profile": {
            "info_cache": {
                "Profile 1": {...},
                "Profile 2": {...},
                ...
            }
        }
        """
        Files.assert_exists(filepath)
        profiles: list[dict[str, str]] = []
        parent_container_name = 'profile'
        child_container_name = 'info_cache'

        data = Files.read_json(filepath)

        try:
            parent_container = data[parent_container_name]
            child_container: dict[str, Any] = parent_container[child_container_name]
        except KeyError as err:
            raise ValueError(err) from err
        for key, profile in child_container.items():
            name = profile.get('name')
            profiles.append({'name': name, 'key': key})
        return profiles

    @staticmethod
    def gecko(filepath: Path) -> list[dict[str, str]]:
        Files.assert_exists(filepath)
        profiles: list[dict[str, str]] = []

        logger.debug(f"filepath from 'read_gecko_type'={filepath!r}")
        parser = Files.read_ini(filepath)

        for section in parser.sections():
            if 'Profile' not in section:
                continue
            name = parser.get(section, 'Name')
            profiles.append({'name': name, 'key': name})
        return profiles


@dataclass
class ProfileManager:
    _profiles: dict[str, Profile] = field(default_factory=dict)
    _data: list[dict[str, str]] = field(default_factory=list)
    _browser: Browser = field(init=False)

    @property
    def file(self) -> Path:
        return Path(self._browser.path).expanduser()

    def add(self, profile: Profile) -> None:
        self._profiles[profile.name] = profile

    def get(self, name: str) -> Profile:
        # FIX: better way to handle incognito profile
        if name.lower() == 'incognito':
            return self.incognito()
        return self._profiles[name]

    def load(self) -> None:
        data = self._browser.flags.data_extractor(self.file)
        for profile in data:
            profile['command'] = self._browser.flags.launch(profile['key'])
            self.add(self.new(profile))
        self.add(self.incognito())

    def incognito(self) -> Profile:
        return Profile(
            name='Incognito',
            key='Incognito',
            cmd=self._browser.flags.incognito,
        )

    @staticmethod
    def new(data: dict[str, str]) -> Profile:
        return Profile(name=data['name'], key=data['key'], cmd=data['command'])

    def select(self, menu: MenuInterface) -> Profile:
        selected, keycode = menu.prompt(
            items=tuple(self._profiles), prompt=f'{self._browser.name}> '
        )

        if keycode == 1 or selected is None:
            sys.exit(1)

        return self.get(selected)


@dataclass
class Browser:
    name: str
    command: str
    path: str
    engine: str
    enabled: bool
    profiles: ProfileManager = field(default_factory=ProfileManager)
    default: bool = False
    _flags: Flags | None = None

    def __post_init__(self) -> None:
        self.profiles._browser = self

    @property
    def flags(self) -> Flags:
        if not self._flags:
            self._flags = _TYPES[self.engine](cmd=self.command)
        return self._flags

    @property
    def status(self) -> str:
        if shutil.which(self.command) is None:
            return RED.format('not found')
        return CYAN.format('enable') if self.enabled else ORANGE.format('disable')

    def disable(self) -> Self:
        self.enabled = False
        return self

    def enable(self) -> Self:
        self.enabled = True
        return self

    def update(self) -> Self:
        Files.save_browser(HOME, self)
        return self

    def open(self, url: str) -> int:
        return Process.run(f'{self.flags.new_tab} {url}')

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


@dataclass
class BrowserCollection:
    _collection: dict[str, Browser] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self._collection)

    def get(self, name: str) -> Browser:
        name = name.lower()
        logger.debug(f'browser {name!r} requested')
        try:
            browser = self._collection[name]
        except KeyError:
            log_error_and_exit(f'browser {name!r} not found')
        return browser

    def add(self, browser: Browser) -> None:
        logger.debug(f'browser {browser.name!r} added')
        self._collection[browser.name.lower()] = browser

    @staticmethod
    def new(data: dict[str, Any]) -> Browser:
        logger.debug(f'browser {data!r} added')
        return Browser(**data)

    def found(self) -> dict[str, Browser]:
        browsers = self._collection.values()
        return {b.name: b for b in browsers if shutil.which(b.command) and b.enabled}

    def list(self) -> list[Browser]:
        return list(self._collection.values())

    def select(self, menu: MenuInterface, browsers: dict[str, Browser] | None = None) -> Browser:
        if browsers is None:
            browsers = self._collection

        if not browsers:
            err_msg = 'no browser found'
            raise NoBrowserFoundError(err_msg)

        selected, keycode = menu.prompt(
            items=tuple(browsers),
            prompt=f'{__appname__}> ',
        )

        # FIX: do not exit program
        if keycode == 1 or selected is None:
            sys.exit(1)

        return self.get(selected)

    def load_json_files(self, home: Path) -> None:
        for file in home.glob('*.json'):
            try:
                data = Files.read_json(file)
                validate_data_from_json(data)
            except InvalidJSONError as err:
                err_msg = f'file={file.name} is not a valid JSON.\n{err}'
                raise InvalidJSONError(err_msg) from err
            browser = self.new(data)
            self.add(browser)

    def load_defaults(self) -> Self:
        self.add(firefox)
        self.add(chromium)
        self.add(librewolf)
        self.add(brave)
        self.add(google_chrome)
        return self

    def status(self) -> None:
        header = ('name', 'command', 'engine', 'status')
        table = [header]
        for browser in self.list():
            table.append((browser.name, browser.command, browser.engine, browser.status))
        print_table(table)

    def table(self) -> None:
        header = ('name', 'command', 'engine', 'path', 'enabled', 'status')
        table = [header]
        browsers = self.list()
        if len(browsers) == 0:
            return

        for browser in browsers:
            enabled = 'yes' if browser.enabled else 'no'
            row = (
                browser.name,
                browser.command,
                browser.engine,
                shorten_path_str(browser.path, length=80, parts=4),
                enabled,
                browser.status,
            )
            table.append(row)

        print_table(table)


firefox = Browser(
    name='Firefox',
    command='firefox',
    path='~/.mozilla/firefox/profiles.ini',
    engine='gecko',
    enabled=True,
)
chromium = Browser(
    name='Chromium',
    command='chromium',
    path='~/.config/chromium/Local State',
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
brave = Browser(
    name='Brave',
    command='brave',
    path='~/.config/BraveSoftware/Brave-Browser/Local State',
    engine='blink',
    enabled=True,
)
google_chrome = Browser(
    name='Chrome',
    command='google-chrome',
    path='~/.config/google-chrome/Local State',
    engine='blink',
    enabled=True,
)


class Process:
    @staticmethod
    def run(commands: str) -> int:
        logger.debug(f'executing from run: {commands!r}')
        process = subprocess.run(
            shlex.split(commands),
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
        logger.debug(f'execute::{process!r}')
        return process.returncode


def parse_and_exit(
    args: argparse.Namespace,
    browsers: BrowserCollection,
    menu: MenuInterface,
) -> None:
    if args.test:
        logger.debug('testing mode')
        sys.exit(0)

    if args.help:
        print(HELP)
        sys.exit(0)

    if args.version:
        print(__appname__, __version__)
        sys.exit(0)

    if args.list:
        browsers.status()
        sys.exit(0)

    if args.table:
        browsers.table()
        sys.exit(0)

    if args.enable:
        if not args.browser:
            log_error_and_exit('enable: browser not specified')
        browser = browsers.get(args.browser)
        browser.enable().update()
        logger.debug(f'browser {browser.name!r} enabled')
        sys.exit(0)

    if args.disable:
        if not args.browser:
            log_error_and_exit('disable: browser not specified')
        browser = browsers.get(args.browser)
        browser.disable().update()
        logger.debug(f'browser {browser.name!r} disabled')
        sys.exit(0)


def main() -> int:
    setup = Setup()
    setup.files()

    args = setup.args()
    menu = setup.menu(args.menu)

    try:
        browsers = BrowserCollection()
        browsers.load_defaults().load_json_files(HOME)
        parse_and_exit(args, browsers, menu)

        browser = (
            browsers.get(args.browser) if args.browser else browsers.select(menu, browsers.found())
        )
        browser.profiles.load()

        profile = browser.profiles.select(menu)
        if args.url:
            return profile.open(args.url)
        return profile.launch()
    except EXCEPTIONS as err:
        menu.prompt(items=[err], prompt='PyBrowserErr>')
        log_error_and_exit(str(err))
    return 1


if __name__ == '__main__':
    sys.exit(main())
