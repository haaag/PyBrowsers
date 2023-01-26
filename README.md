# Profile Launcher: A Python Script for Effortless Browser Profile Management

### ⭐ About 

This Python script allows you to quickly launch `browser profiles` without having to manually navigate through the browser's settings.
It reads the profile information from each browser's config directory and presents them as options for launch.
This can save you time and improve your workflow if you frequently switch between multiple profiles.

The script currently supports all Chromium and Gecko-based browsers that use `XDG config` and `~/.mozilla` directories. 

If you need to add support for other browsers, please refer to [Add browser](#add-browser) 

### 📦 Installation

```bash
# Just clone repository
$ git clone "https://github.com/haaag/browser-profiles-launcher"
$ cd browser-profiles-launcher

# Create virtual environment & source
$ python -m venv .venv
$ source .venv/bin/activate
```

### 🚀 Usage

```bash
usage: Simple script that launches browser with the selected profile. 
[-h] [-b BROWSER] [-v] [-r] [-a]

options:
  -h, --help            show this help message and exit
  -b, --browser         Browser to launch (default: firefox)
  -r, --rofi            Use Rofi (default: dmenu)
  -a, --all             Select from browsers found in your system.
  -v, --verbose         Set logger to DEBUG
```

#### > Use the `-b` or `--browser` option to specify the browser you want to launch

```bash
# Open menu with profiles list on Dmenu (This script defaults to Dmenu as Menu)
$ (.venv) python main.py -b firefox
# or
$ (.venv) python main.py --browser firefox
```

<br>
<img align="center" width="684" height="27" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-dmenu.png?raw=true">
<br>

#### > Use the `-r` or `--rofi` option to specify the launcher you want to use

```bash
$ (.venv) python main.py -b firefox --rofi
```

<img align="center" width="314" height="423" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-rofi.png?raw=true">
<br>

#### > Open all browsers found with Dmenu or Rofi with the argument `--all`

```bash
# Dmenu
$ (.venv) python main.py --all

# Rofi
$ (.venv) python main.py --all --rofi
```

### ➕ Add Browser

You can add a new configuration by modifying the `src/database.py` file accordingly.

#### Example

```python
"google-chrome-unstable": {
    "name": "google-chrome-unstable",
    "profile_command": "--profile-directory='{profile}' --no-default-browser-check",
    "profile_file": "~/.config/google-chrome-unstable/Local State",
    "incognito": "--incognito",
    "type": JSON,
},
```

### 🌐 Browsers

- Firefox
- Chromium
- Google Chrome
- Google Chrome Beta
- Brave
- Waterfox Classic

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
- [X] **Remove** python **dependencies**
