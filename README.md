# Simple python script for launching browser's Profiles

It takes care of reading the profile's file in each browser's config directory. (Tested on linux [Artix](https://artixlinux.org/))

### Tested on the following Browsers

- Firefox
- Chromium
- Google Chrome
- Brave
- Waterfox Classic

## Usage

#### This script defaults to Dmenu as Menu.

#### You can pass as argument `-b` or `--browser-name` to select the profile
~~~bash
# Open menu with profiles list on Dmenu
$ python main.py -b firefox
# or
$ python main.py --browser-name firefox
~~~

<img align="center" width="684" height="27" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-dmenu.png?raw=true">

#### You can pass the argument `--rofi` to call the Rofi menu.
~~~bash
$ python main.py -b firefox --rofi
~~~

<img align="center" width="314" height="423" src="https://github.com/haaag/profiles-browser-python/blob/main/.img/firefox-rofi.png?raw=true">

#### Open all browsers found with Dmenu or Rofi with the argument `--all`
~~~bash
# Dmenu
$ python main.py --all

# Rofi
$ python main.py --all --rofi
~~~

    Usage: main.py [OPTIONS]

      Simple script that launches browser with the selected profile.

    Options:
      -b, --browser-name [firefox|chromium|brave|google-chrome|waterfox-classic]
                                      Give a browser to launch.
      -a, --all                       Show supported browser and profiles.
      --rofi                          Choose profile with Rofi (dmenu Default).
      --show-config                   Show config's dictonary.
      -n, --notification              Show notifications.
      --help                          Show this message and exit.

### Tools Dependencies

- [dmenu](https://tools.suckless.org/dmenu/)
- [rofi](https://github.com/davatorium/rofi)

### Python Dependencies

- [dmenu python](https://github.com/allonhadaya/dmenu-python)
- [python rofi](https://github.com/bcbnz/python-rofi)
- [click](https://palletsprojects.com/p/click/)

### config.json

- `name`: Browser's Name, and __executable__.
- `profile_file`: Absolute path to profiles file.
- `type`: ini or json
- `command`: Command to execute with selected profile.

~~~json
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
~~~
