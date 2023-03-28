# menu.py

from __future__ import annotations

import shlex
import subprocess
from typing import Optional

from pyselector import Menu

from . import helpers

log = helpers.get_logger(__name__)


class Executor:
    def run(self, command: str, args: str) -> Optional[subprocess.Popen]:
        """Run the command with the specified executable."""
        try:
            args_splitted = shlex.split(f"{command} {args}")
            log.debug("running command: '%s'", args_splitted)
            return subprocess.Popen(
                args_splitted, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE
            )

        except subprocess.CalledProcessError as e:
            log.exception(e)
            return None

    def execute(self, command: str, args: str, items: list[str]) -> Optional[str]:
        """Executes the given command with the specified executable and input items."""
        proc = self.run(command, args)
        if proc:
            bytes_items = "\n".join(items).encode()
            selected, _ = proc.communicate(input=bytes_items)
            return selected.decode(encoding="utf-8")
        return None


def get_menu(name: str):
    menu = {
        "rofi": Menu.rofi(),
        "dmenu": Menu.dmenu(),
        "fzf": Menu.fzf(),
    }
    return menu[name]
