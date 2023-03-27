![Python](https://img.shields.io/badge/python-3670A0?style=Flat&logo=python&logoColor=ffdd54)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

# Profile Launcher: A Python Script for Effortless Browser Profile Management

### ⭐ About 

This Python script allows you to quickly launch `browser profiles` without having to manually navigate through the browser's settings.
It reads the profile information from each browser's config directory and presents them as options for launch.
This can save you time and improve your workflow if you frequently switch between multiple profiles.

The script currently supports all Chromium and Gecko-based browsers that use `XDG config` and `~/.mozilla` directories. 


### 📦 Installation

#### > Using `pipx` _(recommended)_

~~~bash
$ pipx install pybrowsers-profiles
~~~

> [pipx Homepage](https://github.com/pypa/pipx)

#### > Using `pip` install

```bash
# Just clone repository
$ git clone "https://github.com/haaag/PyBrowsers-Profiles"
$ cd PyBrowsers-Profiles

# Create virtual environment & source
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install .
```

### 🚀 Usage

```bash
$ pybrowsers --help

[-h] [-b BROWSER] [-v] [-r] [-f] [-t]

usage: Simple script that launches browser with the selected profile. 

options:
  -h, --help            show this help message and exit
  -b, --browser         Browser to launch (default: firefox)
  -r, --rofi            Use Rofi (default: dmenu)
  -f, --found           Select from browsers found in your system.
  -v, --verbose
```

#### > Use the `-b` or `--browser` option to specify the browser you want to launch

```bash
# Open menu with profiles list on Dmenu (This script defaults to Dmenu as Menu)
$ (.venv) pybrowsers -b firefox
# or
$ (.venv) pybrowsers --browser firefox
```

<br>
<img align="center" width="684" height="27" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-dmenu.png?raw=true">
<br>

#### > Use the `-r` or `--rofi` option to specify the launcher you want to use

```bash
$ (.venv) pybrowsers -b firefox --rofi
```

<img align="center" width="314" height="423" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-rofi.png?raw=true">
<br>

#### > Open all browsers found with Dmenu or Rofi with the argument `--found`

```bash
# Dmenu
$ (.venv) pybrowsers --found

# Rofi
$ (.venv) pybrowsers --found --rofi
```

### ➕ Add Browser

You can add a new configuration by modifying the `src/database.py` file accordingly.

#### Example

```python
"ungoogled-chromium": {
    "name": "ungoogled-chromium",
    "command": "ungoogled-chromium",
    "profile_command": "--profile-directory='{profile}' --no-default-browser-check",
    "profile_file": "~/.config/chromium/Local State",
    "incognito": "--incognito",
    "type": JSON,
}
```

### 🌐 Browsers

- [Firefox](https://www.mozilla.org/firefox/download/thanks/)
- [LibreWolf](https://librewolf.net/)
- [Ungoogled Chromium](https://github.com/ungoogled-software/ungoogled-chromium)
- [Chromium](https://www.chromium.org/getting-involved/download-chromium/)
- Brave
- Google Chrome
- [Waterfox Classic](https://www.waterfox.net/download/)

### ⚡️ Requirements

- [firefox](https://www.mozilla.org/en-US/firefox/new/)
- [dmenu](https://tools.suckless.org/dmenu/)
- [rofi](https://github.com/davatorium/rofi)

### 🧰 TODO

- [ ] Better way to `add a new browser`
    - Go back to `JSON` file? 
    - Use `sqlite3`?
- [ ] Find a better way to get `Menu` object (maybe factory mode)
- [X] Please, use `pathlib.Path`
