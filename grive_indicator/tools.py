#!/usr/bin/env python3

import os
import json
from pathlib import Path
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import AppIndicator3

GRIVEI_PATH = os.path.abspath(os.path.join(str(Path(__file__).parents[0])))
autostart_file = os.path.join(os.environ['HOME'], '.config', 'autostart', 'grive-indicator.desktop')


def getValue(key):
    with open("{}/.grive-indicator".format(os.environ['HOME']), 'r') as json_data:
        data = json.load(json_data)
    return data[key]


def setValue(key, value):
    with open("{}/.grive-indicator".format(os.environ['HOME']), 'r') as json_data:
        data = json.load(json_data)
    with open("{}/.grive-indicator".format(os.environ['HOME']), 'w') as json_data:
        data[key] = value
        json.dump(data, json_data)
    subprocess.Popen(['notify-send', '{} set to {}.'.format(key.capitalize(), value),
                      '--icon={}/drive-dark.png'.format(os.path.abspath(os.path.join(GRIVEI_PATH, "data")))])


def getIcon():
    style = getValue('style')
    if style == 'light' or style == 'dark':
        return os.path.join(GRIVEI_PATH, "data", 'drive-' + style + '.png')
    else:
        return style

ind = AppIndicator3.Indicator.new("Grive Indicator", getIcon(),
                                  AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
ind.set_attention_icon("indicator-messages-new")
