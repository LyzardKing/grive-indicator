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

GRIVEI_PATH = os.path.abspath(os.path.join(str(Path(__file__).parents[0])))
logging.basicConfig(format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
autostart_file = os.path.join(os.environ['HOME'], '.config', 'autostart', 'grive-indicator.desktop')


def runConfigure(folder=None):
    if not folder:
        logger.error("Folder needed. Usage: grive-indicator --folder <folder>")
        selective = subprocess.check_output(['zenity', '--forms',
                                             '--text="Configuration file missing.'
                                             'Add the remote folder to sync(leave blank to sync all)"',
                                             '--add-entry="Remote Folder (selective sync)"'])
        selective = selective.decode().strip()
        folder = subprocess.check_output(['zenity',
                                          '--title="Local Folder"',
                                          '--file-selection',
                                          '--directory'])
        folder = folder.decode().strip()
        if not os.path.isfile(os.path.join(folder, '.grive')):
            result = subprocess.check_output(['zenity',
                                              '--question',
                                              '--text="The  is not currently registered with grive.'
                                              'Do you want to proceed?"'])
            if result == b'':
                # Authenticate with Google Drive
                self.runAuth(folder)
    data = {"style": "dark", "time": 30,
            "folder": folder,
            "selective": selective,
            "upload_speed": '',
            "download_speed": ''}
    with open("{}/.grive-indicator".format(os.environ['HOME']), 'w+') as json_data:
        json.dump(data, json_data)


def runAuth(self, folder):
    LOCK = True
    thread = threading.Thread(target=_runAuth, args=[folder])
    thread.start()
    while not os.path.isfile(os.path.join(folder, '.grive')):
        sleep(3)
    LOCK = False


def _runAuth(self, folder):
    txt = ''
    auth = subprocess.Popen(['grive', '-a'], shell=False, cwd=folder, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    for line in iter(auth.stdout.readline, ''):
        txt += line.decode()
        if 'Please input the authentication code' in txt:
            break
    url = re.search('https.*googleusercontent.com', txt).group(0)
    subprocess.Popen(['xdg-open', url])
    result = subprocess.check_output(['zenity', '--forms', '--add-entry="Auth Code"'])
    auth.stdin.write(result)
    auth.stdin.flush()


def getValue(key):
    try:
        with open("{}/.grive-indicator".format(os.environ['HOME']), 'r') as json_data:
            data = json.load(json_data)
        return data[key]
    except FileNotFoundError:
        runConfigure()
        return getValue(key)


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
