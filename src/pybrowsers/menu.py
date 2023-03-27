# menu.py

import shlex
import subprocess
import sys
from typing import Optional
from typing import Protocol

from . import helpers

log = helpers.get_logger(__name__)

# TODO:
# [ ] find a better way to get Menu object (factory mode)


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


class Menu(Protocol):
    command: str
    executor: Executor

    def show(self, items: list[str], prompt: str) -> str:
        ...


class Rofi:
    def __init__(self) -> None:
        self.command = "rofi -dmenu"
        self.executor = Executor()

    def show(self, items: list[str], prompt: str) -> str:
        commands = f"-i -l 10 -p '{prompt}'"
        selected = self.executor.execute(self.command, commands, items)
        if not selected:
            sys.exit(1)
        return selected.strip()


class Dmenu:
    def __init__(self) -> None:
        self.command = "dmenu"
        self.executor = Executor()

    def show(self, items: list[str], prompt: str) -> str:
        # commands = f"-i -l 12 -p '{prompt}'"
        commands = f"-i -p '{prompt}'"
        selected = self.executor.execute(self.command, commands, items)
        if not selected:
            sys.exit(1)
        return selected.strip()


class Pavel:
    def __call__(self, executor: Executor, bin: str, commands: str, items: list[str]) -> str:
        selected = executor.execute(bin, commands, items)
        if not selected:
            sys.exit(1)
        return selected.strip()
