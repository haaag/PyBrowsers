# Profile Launcher: A Python Script for Effortless Browser Profile Management

<!--toc:start-->
- [Profile Launcher: A Python Script for Effortless Browser Profile Management](#profile-launcher-a-python-script-for-effortless-browser-profile-management)
    - [Installation](#installation)
    - [Usage](#usage)
      - [Use the `-b` or `--browser-name` option to specify the browser you want to launch](#use-the-b-or-browser-name-option-to-specify-the-browser-you-want-to-launch)
      - [Use the `--rofi` option to specify the launcher you want to use](#use-the-rofi-option-to-specify-the-launcher-you-want-to-use)
      - [Open all browsers found with Dmenu or Rofi with the argument `--all`](#open-all-browsers-found-with-dmenu-or-rofi-with-the-argument-all)
    - [Browsers](#browsers)
    - [Tools Dependencies](#tools-dependencies)
    - [Python Dependencies](#python-dependencies)
    - [config.json](#configjson)
    - [TODO](#todo)
<!--toc:end-->

This Python script allows you to quickly launch `browser profiles` without having to manually navigate through the browser's settings.
It reads the profile information from each browser's config directory and presents them as options for launch.
This can save you time and improve your workflow if you frequently switch between multiple profiles.

### Installation

```bash
# Clone repository
$ git clone "https://github.com/haaag/profiles-browser-python.git"
$ cd profiles-browser-python

# Create virtual environment & source
$ python -m venv .venv
$ source .venv/bin/activate

# Install requirements
$ (.venv) pip install -r requirements.txt
```

### Usage

```bash
Usage: main.py [OPTIONS]

    Simple script that launches browser with the selected profile.

Options:
    -b, --browser-name              Browser to launch
    -a, --all                       Show supported browser and profiles.
    --rofi                          Choose profile with Rofi (dmenu Default).
    --show-config                   Show config's dictonary.
    -n, --notification              Show notifications.
    --help                          Show this message and exit.
```

#### Use the `-b` or `--browser-name` option to specify the browser you want to launch

```bash
# Open menu with profiles list on Dmenu (This script defaults to Dmenu as Menu)
$ python main.py -b firefox
# or
$ python main.py --browser-name firefox
```

<br>
<img align="center" width="684" height="27" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-dmenu.png?raw=true">
<br>

#### Use the `--rofi` option to specify the launcher you want to use

```bash
$ python main.py -b firefox --rofi
```

<img align="center" width="314" height="423" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-rofi.png?raw=true">
<br>

#### Open all browsers found with Dmenu or Rofi with the argument `--all`

```bash
# Dmenu
$ python main.py --all

# Rofi
$ python main.py --all --rofi
```

### Browsers

- Firefox
- Chromium
- Google Chrome
- Brave
- Waterfox Classic

The script currently supports all Chromium and Gecko-based browsers that use `XDG config` and `~/.mozilla` directories. If you need to add support for other browsers, you can do so by modifying the [config.json](#configjson) file accordingly.

### Tools Dependencies

- [dmenu](https://tools.suckless.org/dmenu/)
- [rofi](https://github.com/davatorium/rofi)

### Python Dependencies

- [dmenu python](https://github.com/allonhadaya/dmenu-python)
- [python rofi](https://github.com/bcbnz/python-rofi)
- [click](https://palletsprojects.com/p/click/)

### config.json

- `name`: Browser's Name, and **executable**.
- `profile_file`: Absolute path to profiles file.
- `type`: ini or json
- `command`: Command to execute with selected profile.

```json
{
  "browsers": [
    {
      "name": "firefox",
      "profile_file": "~/.mozilla/firefox/profiles.ini",
      "type": "ini",
      "command": "{executable} -P {profile}"
    },
    {
      "name": "waterfox-classic",
      "profile_file": "~/.waterfox/profiles.ini",
      "type": "ini",
      "command": "{executable} -P {profile}"
    },
    {
      "name": "chromium",
      "profile_file": "~/.config/chromium/Local State",
      "type": "json",
      "command": "{executable} --profile-directory='{profile}' --no-default-browser-check"
    },
    {
      "name": "google-chrome",
      "profile_file": "~/.config/google-chrome/Local State",
      "type": "json",
      "command": "{executable} --profile-directory='{profile}' --no-default-browser-check"
    },
    {
      "name": "brave",
      "profile_file": "~/.config/BraveSoftware/Brave-Browser/Local State",
      "type": "json",
      "command": "{executable} --profile-directory='{profile}' --no-default-browser-check"
    }
  ]
}
```

### TODO

- [ ] Please, use `pathlib.Path`
