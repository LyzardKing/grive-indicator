# -*- coding: utf-8 -*-
# Copyright (C) 2017  Galileo Sartor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
from pathlib import Path
import subprocess
import requests
import logging
import gi
import configparser
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Notify, GdkPixbuf, Gdk
from gi.repository import AppIndicator3
from .UI import InfoDialog, EntryDialog
import shutil
import re


root_dir = os.path.dirname(os.path.abspath(os.path.join(str(Path(__file__)))))
config_file = os.path.join(GLib.get_user_config_dir(), 'grive_indicator.conf')
logger = logging.getLogger(__name__)
Notify.init(__name__)
autostart_file = os.path.join(GLib.get_user_config_dir(), 'autostart', 'grive-indicator.desktop')
griveignore_init = "# Set rules For selective sync.\n"\
                   "# Check the man page or\n"\
                   "# https://github.com/vitalif/grive2#griveignore"


class Config:

    def __init__(self):
        self.config = configparser.ConfigParser()

    def config(self):
        self.config.read(config_file)
        return self.config

    def getValue(self, key):
        self.config.read(config_file)
        return self.config['DEFAULT'][key]

    def setValue(self, key, value):
        logger.debug('Set config {} to {}'.format(key, value))
        self.config.read(config_file)
        self.config['DEFAULT'][key] = value
        with open(config_file, 'w') as configfile:
            self.config.write(configfile)
        notification = Notify.Notification.new('{} set to {}.'.format(key.capitalize(), value))
        notification.set_icon_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(getAlertIcon()))
        notification.show()


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def is_connected(url='https://drive.google.com/', timeout=10):
    try:
        r = requests.get(url=url, timeout=timeout)
        if r.status_code != 200:
            raise Exception
    except:
        logger.error('No internet connection available. Skipping sync.')
        return False
    return True


def runConfigure(folder, selective=None):
    if os.path.exists(config_file):
        logger.info('A config file exists. Override? Y/n')
        if input().lower() != 'y':
            return
    _runConfigure(folder, selective)
    if not os.path.isfile(os.path.join(folder, '.grive')):
        response = InfoDialog.main(parent=None, title='Warning',
                                   label='The  is not currently registered with grive. Do you want to proceed?')
        if response == Gtk.ResponseType.OK:
            logger.debug('Confirm auth')
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
    Gtk.show_uri(None, url, Gdk.CURRENT_TIME)
    auth_response = EntryDialog.main(parent=None, title='Warning', label='Insert the Auth Code')
    logger.debug(auth_response)
    auth.stdin.write(auth_response.encode())
    auth.stdin.flush()


def getAlertIcon():
    return os.path.join(root_dir, "data", 'drive-dark.svg')


def getIcon():
    try:
        style = Config().getValue('style')
    except Exception as e:
        logger.error(e)
        style = 'dark'
    if style == 'light' or style == 'dark':
        icon = os.path.join(root_dir, "data", 'drive-' + style + '.svg')
        return icon
    else:
        return style


def show_notify(line):
    key = line.split('"')[2]
    value = line.split('"')[1]
    notification = Notify.Notification.new('{} {}'.format(key.capitalize(), value))
    notification.set_icon_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(getAlertIcon()))
    notification.show()


ind = AppIndicator3.Indicator.new("Grive Indicator", getIcon(),
                                  AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
ind.set_attention_icon("indicator-messages-new")
