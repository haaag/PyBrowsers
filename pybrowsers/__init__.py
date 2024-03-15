#!/usr/bin/env python3

from __future__ import annotations

import logging
import os
import sys
import textwrap
from pathlib import Path

from pyselector import Menu

logger = logging.getLogger(__name__)

# TODO:
# - [X] Add open-url option


def log_error_and_exit(msg: str) -> None:
    logger.error(f':{msg}:')
    sys.exit(1)


__version__ = '0.0.10'
__appname__ = 'PyBrowsers'
DOT = '\u00b7'
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
        -l, --list          Show browsers list and status
        -t, --table         Show browsers list with detail
        -m, --menu          Select menu (default: dmenu)
        -f, --found         Browsers found
        -o, --open          Open <URL> in browser
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
