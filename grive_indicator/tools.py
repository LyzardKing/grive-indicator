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
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Notify, GdkPixbuf
from gi.repository import AppIndicator3
from .UI import InfoDialog, EntryDialog
from time import sleep
import threading
import shutil
import re


root_dir = os.path.dirname(os.path.abspath(os.path.join(str(Path(__file__)))))
config_file = os.path.join(GLib.get_user_config_dir(), 'grive_indicator.conf')
logger = logging.getLogger(__name__)
Notify.init(__name__)
autostart_file = os.path.join(GLib.get_user_config_dir(), 'autostart', 'grive-indicator.desktop')
griveignore_init = "# Set rules For selective sync.\n"\
                   "# Check the man page or"\
                   "https://github.com/vitalif/grive2#griveignore."
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
        notification = Notify.Notification.new('{} set to {}.'.format(key.capitalize(), value))
        notification.set_icon_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(getAlertIcon()))
        notification.show()


def runConfigure(folder, selective=None):
    _runConfigure(folder, selective)
    if not os.path.isfile(os.path.join(folder, '.grive')):
        response = InfoDialog.main(parent=None, title='Warning',
                                   label='The  is not currently registered with grive. Do you want to proceed?')
        if response == Gtk.ResponseType.OK:
            logger.debug('Confirm auth')
            LOCK = True
            # Authenticate with Google Drive
            runAuth(folder)


def _runConfigure(folder, selective=None):
    logger.debug('Saving configurations: folder:%s selective:%s' % (folder, selective))
    shutil.copy(os.path.join(root_dir, 'data', 'grive_indicator.conf'), config_file)
    with open(os.path.join(folder, '.griveignore'), 'w') as griveignore:
        griveignore.write(selective)
    conf = Config()
    conf.setValue('folder', folder)
    conf.setValue('selective', str(selective is not None))
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
    response = EntryDialog.main(parent=None, title='Warning', label='Insert the Auth Code')
    logger.debug(response)
    auth.stdin.write(response.encode())
    auth.stdin.flush()
    LOCK = False


def getAlertIcon():
    return os.path.join(root_dir, "data", 'drive-dark.png')


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
