#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import logging
import shlex
import shutil
import subprocess
import sys
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

import pybrowsers

if TYPE_CHECKING:
    from pyselector.interfaces import MenuInterface

logger = logging.getLogger(__name__)

# TODO:
# - [X] Add open-url option


def log_error_and_exit(msg: str) -> None:
    logger.error(f':{msg}:')
    sys.exit(1)


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
        log_error_and_exit(f'key {key!r} not found in {data!r}')


def execute(commands: str) -> int:
    try:
        args = shlex.split(commands)

        completed_process = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
        logger.debug(f'execute::{completed_process!r}')
        return completed_process.returncode
    except subprocess.SubprocessError as e:
        logging.exception(e)
        raise e


class Setup:
    def home(self) -> None:
        if pybrowsers.HOME.exists():
            logger.debug(f'directory {pybrowsers.HOME.name!r} already exists')
            return

        logger.debug(f'creating directory {pybrowsers.HOME.name!r}')
        pybrowsers.HOME.mkdir(exist_ok=True)

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
        parser.add_argument('-o', '--open', nargs='?')
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


class Format:
    @staticmethod
    def title(title: str, items: list[str]) -> list[str]:
        return [f'\n> {title}\n', *items]

    @staticmethod
    def bullet(label: str, value: str) -> str:
        return f' {pybrowsers.DOT} {label: <20} {value}'

    @staticmethod
    def json(browser: Browser) -> str:
        return json.dumps(
            {
                'name': browser.name,
                'command': browser.command,
                'path': browser.path,
                'engine': browser.engine,
                'enabled': browser.enabled,
            },
            indent=2,
        )

    @staticmethod
    def table(header: tuple[str, ...], rows: tuple[str, ...]) -> Sequence[tuple[str, ...]]:
        table = [header]
        table.append(rows)
        return table


class Files:
    @staticmethod
    def read_json(filepath: Path) -> dict[str, Any]:
        try:
            logger.debug(f'reading file {filepath.name!r}')
            with filepath.open(encoding='utf-8', mode='r') as file:
                data = json.load(file)
        except FileNotFoundError as _:
            log_error_and_exit(f'JSON file {filepath.name!r} not found')
        except JSONDecodeError as _:
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
    def save(path: Path, browser: Browser) -> None:
        file = path / f'{browser.name.lower()}.json'
        with file.open(mode='w') as f:
            f.write(Format.json(browser))
        return

    @staticmethod
    def assert_exists(file: Path) -> None:
        try:
            if file.is_dir():
                err_msg = f"file '{file!s}' is not a file."
                raise IsADirectoryError(err_msg)
            if not file.exists():
                err_msg = f"file '{file!s}' not found"
                raise FileNotFoundError(err_msg)
        except (FileNotFoundError, IsADirectoryError) as _:
            log_error_and_exit(err_msg)


@dataclass
class Flags:
    @staticmethod
    def incognito(program: str) -> str:
        raise NotImplementedError

    @staticmethod
    def launch(program: str, profile: str) -> str:
        raise NotImplementedError

    @staticmethod
    def data_extractor(path: Path) -> list[dict[str, str]]:
        raise NotImplementedError


class BlinkFlags(Flags):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def incognito(program: str) -> str:
        return f'{program} --incognito'

    @staticmethod
    def launch(program: str, profile: str) -> str:
        return f'{program} --profile-directory={profile!r} --no-default-browser-check'

    @staticmethod
    def data_extractor(path: Path) -> list[dict[str, str]]:
        return ProfileFileReader.blink(path)


class GeckoFlags(Flags):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def incognito(program: str) -> str:
        return f'{program} --private-window'

    @staticmethod
    def launch(program: str, profile: str) -> str:
        return f'{program} -P {profile!r}'

    @staticmethod
    def data_extractor(path: Path) -> list[dict[str, str]]:
        return ProfileFileReader.gecko(path)


_TYPES: dict[str, type[Flags]] = {
    'blink': BlinkFlags,
    'gecko': GeckoFlags,
}


class Profile(NamedTuple):
    name: str
    key: str
    command: str

    def launch(self) -> int:
        return execute(self.command)

    def open(self, url: str) -> int:
        return execute(f'{self.command} {url}')


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
        return self._profiles[name]

    def load(self) -> None:
        data = self._browser.flags().data_extractor(self.file)
        for profile in data:
            profile['command'] = self._browser.flags().launch(
                self._browser.command, profile['key']
            )
            self.add(self.new(profile))
        self.add(self.incognito())

    def incognito(self) -> Profile:
        # FIX:
        return Profile(
            name='Incognito',
            key='Incognito',
            command=self._browser.flags().incognito(self._browser.command),
        )

    @staticmethod
    def new(data: dict[str, str]) -> Profile:
        return Profile(name=data['name'], key=data['key'], command=data['command'])

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

    def __post_init__(self) -> None:
        self.profiles._browser = self

    def flags(self) -> type[Flags]:
        return _TYPES[self.engine]

    @property
    def status(self) -> str:
        if shutil.which(self.command) is None:
            return pybrowsers.RED.format('not found')
        return (
            pybrowsers.CYAN.format('enable')
            if self.enabled
            else pybrowsers.ORANGE.format('disable')
        )

    def disable(self) -> Self:
        self.enabled = False
        return self

    def enable(self) -> Self:
        self.enabled = True
        return self

    def update(self) -> Self:
        Files.save(pybrowsers.HOME, self)
        return self


@dataclass
class BrowserCollection:
    _collection: dict[str, Browser] = field(default_factory=dict)

    def get(self, name: str) -> Browser:
        name = name.lower()
        logger.debug(f'browser {name!r} requested')
        try:
            browser = self._collection[name]
        except KeyError as _:
            log_error_and_exit(f'browser {name!r} not found')
        return browser

    def add(self, browser: Browser) -> None:
        logger.debug(f'browser {browser.name!r} added')
        self._collection[browser.name.lower()] = browser

    @staticmethod
    def new(data: dict[str, Any]) -> Browser:
        logger.debug(f'browser {data!r} added')
        validate_data_from_json(data)
        return Browser(**data)

    def found(self) -> dict[str, Browser]:
        browsers = self._collection.values()
        return {b.name: b for b in browsers if shutil.which(b.command) and b.enabled}

    def list(self) -> list[Browser]:
        return list(self._collection.values())

    def select(self, menu: MenuInterface, browsers: dict[str, Browser] | None = None) -> Browser:
        if browsers is None:
            browsers = self.found()

        if not browsers:
            browsers = {
                'NothingFound': Browser(
                    name='Not found', command='notfound', path='', engine='', enabled=True
                )
            }

        selected, keycode = menu.prompt(
            items=tuple(browsers), prompt=f'{pybrowsers.__appname__}> '
        )

        if keycode == 1 or selected is None:
            sys.exit(1)

        return self.get(selected)

    def load_json_files(self, home: Path) -> None:
        for file in home.glob('*.json'):
            data = Files.read_json(file)
            browser = self.new(data)
            self.add(browser)

    def status(self) -> None:
        header = ('name', 'command', 'engine', 'status')
        table = [header]
        for browser in self.list():
            table.append((browser.name, browser.command, browser.engine, browser.status))
        print_table(table)

    def table(self) -> None:
        header = ('name', 'command', 'engine', 'path', 'enabled', 'status')
        table = [header]
        for browser in self.list():
            enabled = 'yes' if browser.enabled else 'no'
            row = (
                browser.name,
                browser.command,
                browser.engine,
                f'{browser.path!r}',
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


def defaults(browsers: BrowserCollection) -> BrowserCollection:
    browsers.add(firefox)
    browsers.add(chromium)
    browsers.add(librewolf)
    browsers.add(brave)
    browsers.add(google_chrome)
    return browsers


def parse_and_exit(args: argparse.Namespace, browsers: BrowserCollection) -> None:
    if args.test:
        logger.debug('testing mode')
        sys.exit(0)

    if args.help:
        print(pybrowsers.HELP)
        sys.exit(0)

    if args.version:
        print(pybrowsers.__appname__, pybrowsers.__version__)
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
        sys.exit(0)

    if args.disable:
        if not args.browser:
            log_error_and_exit('disable: browser not specified')
        browser = browsers.get(args.browser)
        browser.disable().update()
        sys.exit(0)


def main() -> int:
    setup = Setup()
    setup.home()
    args = setup.args()

    browsers = BrowserCollection()
    browsers = defaults(browsers)
    browsers.load_json_files(pybrowsers.HOME)

    parse_and_exit(args, browsers)

    menu = setup.menu(args.menu)

    browser = browsers.get(args.browser) if args.browser else browsers.select(menu)
    browser.profiles.load()

    if args.open:
        return browser.profiles.select(menu).open(args.open)

    return browser.profiles.select(menu).launch()


if __name__ == '__main__':
    sys.exit(main())
