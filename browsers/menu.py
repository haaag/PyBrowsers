import sys
from typing import Any, Protocol

import dmenu
from rofi import Rofi


class Menu(Protocol):
    menu: Any | Rofi

    def show_items(self, items: list[str], prompt: str = "profiles > ") -> str:
        raise NotImplementedError()

    def error(self, message: str) -> None:
        raise NotImplementedError()


class RofiMenu:
    def __init__(self) -> None:
        self.menu = Rofi()

    def show_items(self, items: list[str], prompt: str = "profiles > ") -> str:
        index, key = self.menu.select(prompt, items)

        # If the user hits escape, return -1
        if key == -1:
            sys.exit(1)

        return items[index]

    def error(self, message: str) -> None:
        return self.menu.exit_with_error(message)


class DmenuMenu:
    def __init__(self) -> None:
        self.menu = dmenu

    def show_items(self, items: list[str], prompt: str = "profiles > ") -> str:
        selected = self.menu.show(items, prompt=prompt)
        return selected

    def error(self, message: str) -> None:
        self.menu.show([message], prompt="Error > ")
        sys.exit(1)


class CurseMenu:
    def __init__(self) -> None:
        raise NotImplementedError()


class GtkMenu:
    def __init__(self) -> None:
        raise NotImplementedError()
