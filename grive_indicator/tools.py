#!/usr/bin/env python3

import os
import json
from pathlib import Path
import subprocess
import logging
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import AppIndicator3
from grive_indicator import UI
from time import sleep
import threading
import re


GRIVEI_PATH = os.path.abspath(os.path.join(str(Path(__file__).parents[0])))
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
autostart_file = os.path.join(os.environ['HOME'], '.config', 'autostart', 'grive-indicator.desktop')
LOCK = False


def runConfigure(folder, selective=None):
    if not selective:
        selective = ''
    _runConfigure(folder, selective)
    if not os.path.isfile(os.path.join(folder, '.grive')):
        response = UI.InfoDialog.main(parent=None,
                                      label='The  is not currently registered with grive. Do you want to proceed?')
        if response == Gtk.ResponseType.OK:
            logger.debug('Confirm auth')
            LOCK = True
            # Authenticate with Google Drive
            runAuth(folder)


def _runConfigure(folder, selective=''):
    logger.debug('Saving configurations: folder:%s selective:%s' % (folder, selective))
    data = {"style": "dark", "time": 30,
            "folder": folder,
            "selective": selective,
            "upload_speed": '',
            "download_speed": ''}
    with open("{}/.grive-indicator".format(os.environ['HOME']), 'w+') as json_data:
        json.dump(data, json_data)


def runAuth(folder):
    LOCK = True
    _runAuth(folder)


def _runAuth(folder):
    txt = ''
    auth = subprocess.Popen(['grive', '-a', '--dry-run'],
                            shell=False,
                            cwd=folder,
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    for line in iter(auth.stdout.readline, ''):
        txt += line.decode()
        if 'Please input the authentication code' in txt:
            break
    url = re.search('https.*googleusercontent.com', txt).group(0)
    subprocess.Popen(['xdg-open', url])
    response = UI.EntryDialog.main(parent=None, label='Insert the Auth Code')
    logger.debug(response)
    auth.stdin.write(response.encode())
    auth.stdin.flush()
    LOCK = False


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
    try:
        style = getValue('style')
    except:
        style = 'dark'
    if style == 'light' or style == 'dark':
        return os.path.join(GRIVEI_PATH, "data", 'drive-' + style + '.png')
    else:
        return style

ind = AppIndicator3.Indicator.new("Grive Indicator", getIcon(),
                                  AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
ind.set_attention_icon("indicator-messages-new")
