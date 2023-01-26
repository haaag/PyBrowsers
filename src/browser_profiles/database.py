# data.py

from .datatypes import INI
from .datatypes import JSON
from .datatypes import BrowserCollection

BROWSERS: BrowserCollection = {
    "firefox": {
        "command": "firefox",
        "profile_command": "-P {profile}",
        "profile_file": "~/.mozilla/firefox/profiles.ini",
        "incognito": "--private-window",
        "type": INI,
    },
    "waterfox-classic": {
        "command": "waterfox-classic",
        "profile_command": "-P {profile}",
        "profile_file": "~/.waterfox/profiles.ini",
        "incognito": "--private-window",
        "type": INI,
    },
    "librewolf": {
        "command": "librewolf",
        "profile_command": "-P {profile}",
        "profile_file": "~/.librewolf/profiles.ini",
        "incognito": "--private-window",
        "type": INI,
    },
    "chromium": {
        "command": "chromium",
        "profile_command": "--profile-directory='{profile}' --no-default-browser-check",
        "profile_file": "~/.config/chromium/Local State",
        "incognito": "--incognito",
        "type": JSON,
    },
    "google-chrome": {
        "command": "google-chrome",
        "profile_command": "--profile-directory='{profile}' --no-default-browser-check",
        "profile_file": "~/.config/google-chrome/Local State",
        "incognito": "--incognito",
        "type": JSON,
    },
    "google-chrome-beta": {
        "command": "google-chrome-beta",
        "profile_command": "--profile-directory='{profile}' --no-default-browser-check",
        "profile_file": "~/.config/google-chrome-beta/Local State",
        "incognito": "--incognito",
        "type": JSON,
    },
    "google-chrome-unstable": {
        "command": "google-chrome-unstable",
        "profile_command": "--profile-directory='{profile}' --no-default-browser-check",
        "profile_file": "~/.config/google-chrome-unstable/Local State",
        "incognito": "--incognito",
        "type": JSON,
    },
    "brave": {
        "command": "brave",
        "profile_command": "--profile-directory='{profile}' --no-default-browser-check",
        "profile_file": "~/.config/BraveSoftware/Brave-Browser/Local State",
        "incognito": "--incognito",
        "type": JSON,
    },
}
