import shlex
import shutil
import subprocess
from typing import Optional


class BrowserExecutableNotFoundError(Exception):
    def __init__(self, name: str):
        self.message = f"Executable for '{name}' browser not found."
        super().__init__(self.message)


class Executor:
    def __init__(self, name: str, notification: bool = False) -> None:
        self.name = name
        self.notification = notification

    def run(self, command_str: str) -> subprocess.Popen[bytes]:
        command: list[str] = self.split(command_str)
        return subprocess.Popen(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    @property
    def bin(self) -> Optional[str]:
        executable = shutil.which(self.name)
        if not executable:
            raise BrowserExecutableNotFoundError(self.name)
        return executable

    def split(self, command: str) -> list[str]:
        return shlex.split(command)

    def send_notification(self, message: str) -> None:
        if not self.notification:
            return None

        notification_str = (f"notify-send '{self.name.capitalize()} profiles script' '{message}'")

        self.run(notification_str)
