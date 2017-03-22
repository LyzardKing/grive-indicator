#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import subprocess
import logging
import gi
import configparser
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import AppIndicator3
from grive_indicator.UI import InfoDialog, EntryDialog
from xdg.BaseDirectory import xdg_config_home
from time import sleep
import threading
import shutil
import re


root_dir = os.path.dirname(os.path.abspath(os.path.join(str(Path(__file__)))))
config_file = os.path.join(GLib.get_user_config_dir(), 'grive_indicator.conf')
logger = logging.getLogger(__name__)
autostart_file = os.path.join(GLib.get_user_config_dir(), 'autostart', 'grive-indicator.desktop')
LOCK = False


class Config:

    def __init__(self):
        self.config = configparser.ConfigParser()

    def config():
        return self.config

    def getValue(self, key):
        self.config.read(config_file)
        return self.config['DEFAULT'][key]

    def setValue(self, key, value):
        self.config.read(config_file)
        self.config['DEFAULT'][key] = value
        with open(config_file, 'w') as configfile:
            self.config.write(configfile)
        subprocess.Popen(['notify-send', '{} set to {}.'.format(key.capitalize(), value),
                          '--icon={}/drive-dark.png'.format(os.path.abspath(os.path.join(root_dir, "data")))])


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
    shutil.copy(os.path.join(root_dir, 'data', 'grive_indicator.conf'), config_file)
    conf = Config()
    conf.setValue('folder', folder)
    conf.setValue('selective', selective)
    with open(config_file, 'w') as configfile:
        conf.config.write(configfile)


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


def getIcon():
    try:
        style = Config().getValue('style')
        logger.debug('Style: %s.' % style)
    except Exception as e:
        logger.error(e)
        style = 'dark'
    if style == 'light' or style == 'dark':
        icon = os.path.join(root_dir, "data", 'drive-' + style + '.png')
        return icon
    else:
        return style

ind = AppIndicator3.Indicator.new("Grive Indicator", getIcon(),
                                  AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
ind.set_attention_icon("indicator-messages-new")
