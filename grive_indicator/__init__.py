#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
import argparse
import os
import shutil
import subprocess
import signal
import sys
import site
import re
from concurrent import futures
import logging
from time import sleep
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import AppIndicator3
from gi.repository import GLib
from pathlib import Path
from datetime import datetime
from multiprocessing import Process
from subprocess import CalledProcessError
from contextlib import suppress
from grive_indicator.UI import settings, configure, InfoDialog
from grive_indicator.tools import getIcon, root_dir, ind, Config, config_file, is_connected, runConfigure

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Singleton
app = Gio.Application(application_id="foo.bar", flags=Gio.ApplicationFlags.FLAGS_NONE)

def on_startup(instance):
    GriveIndicator()

def on_activate(instance):
    pass

app.connect('startup', on_startup)
app.connect('activate', on_activate)

class GriveIndicator():

    def __init__(self):
        parser = argparse.ArgumentParser(description='Grive Indicator.')
        parser.add_argument('--folder', '-f', action='store', help='destination folder')
        parser.add_argument('--selective', '-s', action='store', help='comma separated list of (regex) files to not sync')
        # TODO: Add auth parameter
        args = parser.parse_args()
        folder = args.folder
        selective = args.selective

        self.menu_setup()
        ind.set_menu(self.menu)
        if folder:
            if selective:
                selective = selective.replace(',', '\n')
            runConfigure(folder, selective)
        if not os.path.exists(config_file):
            logger.debug('Setting config file %s.' % config_file)
            configure.main()
        else:
            self.syncDaemon()
        Gtk.main()

    def menu_setup(self):
        self.menu = Gtk.Menu()

        self.lastSync_item = Gtk.MenuItem('Not Available')
        self.lastSync_item.set_sensitive(False)
        self.lastSync_item.show()

        self.syncNow_item = Gtk.MenuItem("Sync now")
        self.syncNow_item.connect("activate", self.syncNow)
        self.syncNow_item.show()

        self.Remote_item = Gtk.MenuItem("Remote Google Drive")
        self.Remote_item.connect("activate", self.openRemote)
        self.Remote_item.show()

        self.Local_item = Gtk.MenuItem("Local Folder")
        self.Local_item.connect("activate", self.openLocal)
        self.Local_item.show()

        self.Settings_item = Gtk.MenuItem("Preferences")
        self.Settings_item.connect("activate", self.settings)
        self.Settings_item.show()

        self.Quit_item = Gtk.MenuItem("Quit")
        self.Quit_item.connect("activate", self.Quit)
        self.Quit_item.show()

        self.seperator_item = Gtk.SeparatorMenuItem()
        self.seperator_item.show()

        self.menu.append(self.lastSync_item)
        self.menu.append(self.syncNow_item)
        self.menu.append(self.seperator_item)
        self.menu.append(self.Remote_item)
        self.menu.append(self.Local_item)
        self.menu.append(self.seperator_item)
        self.menu.append(self.Settings_item)
        self.menu.append(self.seperator_item)
        self.menu.append(self.Quit_item)

    def refresh(self):
        if is_connected() is True:
            self.syncNow(None)
        GLib.timeout_add_seconds(60 * int(Config().getValue('time')), self.refresh)

    def syncDaemon(self):
        executor = futures.ThreadPoolExecutor(max_workers=1)
        self.future = executor.submit(self.refresh)

    def syncNow(self, widget):
        self.lastSync_item.set_label('Syncing...')
        folder = Config().getValue('folder')
        grive_cmd = ['grive']
        upload_speed = Config().getValue('upload_speed')
        if upload_speed != '':
            grive_cmd.append('--upload-speed {}'.format(upload_speed))
        download_speed = Config().getValue('download_speed')
        if download_speed != '':
            grive_cmd.append('--download-speed {}'.format(download_speed))
        try:
            logger.debug('Running: {}'.format(grive_cmd))
            subprocess.check_call(grive_cmd, cwd=folder)
            self.lastSync = re.split('T|\.', datetime.now().isoformat())[1]
            self.lastSync_item.set_label('Last sync at ' + self.lastSync)
        except OSError:
            logger.error('Missing grive in PATH')
            Gtk.main_quit()
        except:
            logger.error('Error occurred running grive. Skipping sync.')
            pass

    def openRemote(self, widget):
        Gtk.show_uri(None, "https://drive.google.com", Gdk.CURRENT_TIME)

    def openLocal(self, widget):
        Gtk.show_uri(None, "file://{}".format(Config().getValue('folder')), Gdk.CURRENT_TIME)

    def settings(self, widget):
        settings.main()

    def Quit(self, widget):
        if self.future.running():
            response = InfoDialog.main(parent=None,
                                       title='Warning',
                                       label='Grive is currently syncing. Please wait a moment.')
            if response == Gtk.ResponseType.OK:
                logger.debug('Finishing sync.')
        Gtk.main_quit()


def main():
    app.run()
