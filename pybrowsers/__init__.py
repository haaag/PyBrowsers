from __future__ import annotations

import logging
import os
import tempfile
import textwrap
from pathlib import Path

from pyselector import Menu

logger = logging.getLogger(__name__)


__version__ = '0.0.11'
__appname__ = 'PyBrowsers'
ROOT = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
HOME = ROOT / __appname__.lower()
RUNNING = Path(tempfile.gettempdir()) / f'{__appname__.lower()}-running.json'
DOT_UNICODE = '\u00b7'
HELP = textwrap.dedent(
    f"""    usage: pybrowsers [-l] [-d DISABLE] [-e ENABLE] [-f] [-t]
                      [-m MENU] [-v] [-V] [browser] [-o URL]

    Simple yet powerful script for managing profiles in multiple web browsers.

    options:
        browser             Browser name
        -e, --enable        Enable browser
        -d, --disable       Disable browser
        -r, --running       Browser running and profile
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
