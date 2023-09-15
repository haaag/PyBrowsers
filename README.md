<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=Flat&logo=python&logoColor=ffdd54)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

</div>

## Profile Launcher

### A Python Script for Effortless Browser Profile Management

### ⭐ About

This Python script allows you to quickly launch `browser profiles` without having to manually navigate through the browser's settings.
It reads the profile information from each browser's config directory and presents them as options for launch.
This can save you time and improve your workflow if you frequently switch between multiple profiles.

### 📦 Installation

#### Using `pipx` _(recommended)_

```bash
$ pipx install pybrowsers-profiles
```

> [pipx Homepage](https://github.com/pypa/pipx)

#### Using `pip` install

```bash
# Clone repository
$ git clone "https://github.com/haaag/PyBrowsers"
$ cd PyBrowsers-Profiles

# Create virtual environment & source
$ python -m venv .venv
# or
$ python -m virtualenv .venv
$ source .venv/bin/activate
$ pip install .
```

### 🚀 Usage

```bash
$ pybrowsers --help

usage: pybrowsers [-l] [-d DISABLE] [-e ENABLE] [-f] [-m {{menu}}] [-v] [browser]

Simple script for manage browser's profiles

options:
    browser                     Browser name
    -e, --enable                Enable browser
    -d, --disable               Disable browser
    -f, --found                 Browsers found
    -l, --list                  Browser list and status
    -m, --menu                  Select menu (default: dmenu)
    -h, --help                  Show this help
    -v, --verbose               Verbose mode
```

```bash
# Open menu with profiles list
$ pybrowsers firefox
# Disable browser (won't appear in `found` arg)
$ pybrowsers --disable firefox
# or
$ pybrowsers -d firefox
```

```bash
# Show status list
$ pybrowsers -l

> BROWSERS STATUS
 - Brave            (not found)
 - Chromium         (enabled)
 - Firefox          (disabled)
 - Chrome           (not found)
 - LibreWolf        (enabled)
```

<br>
<img align="center" width="684" height="27" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-dmenu.png?raw=true">
<br>

#### Use the `-m, --menu` option to specify the launcher you want to use _(default: `dmenu`)_

```{bash}
$ pybrowsers firefox --menu rofi
```

<img align="center" width="314" height="423" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-rofi.png?raw=true">
<br>

### ➕ Add Browser

You can add a browser creating a `json` file in `$XDG_DATA_HOME/pybrowsers/` or
`~/.local/share/pybrowsers` _(Maybe in the future, create a interactive menu for add browser)_

#### Example

```{json}
{
  "name": "LibreWolf",
  "command": "librewolf",
  "path": "~/.librewolf/profiles.ini",
  "engine": "gecko",
  "enabled": true
}
```

### 🌐 Browsers

- [Firefox](https://www.mozilla.org/firefox/download/thanks/)
- [LibreWolf](https://librewolf.net/)
- [Chromium](https://www.chromium.org/getting-involved/download-chromium/)
- Brave
- Google Chrome

### ⚡️ Requirements

- [dmenu](https://tools.suckless.org/dmenu/)
- [rofi](https://github.com/davatorium/rofi) _(Optional)_

### 🧰 TODO

- [ ] Update screenshots
- [ ] Create `interactive menu` for adding browser data
- [x] Please, use `pathlib.Path`
- [x] BUG: Issue when the profile name contains spaces
- [x] Add support for `json` files _(Prioritize)_
