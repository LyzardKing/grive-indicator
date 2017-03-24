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
import dbus
import dbus.service
import dbus.mainloop
import dbus.mainloop.glib
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import AppIndicator3
from gi.repository import GLib
from pathlib import Path
from datetime import datetime
from multiprocessing import Process
from subprocess import CalledProcessError
from contextlib import suppress
from grive_indicator.UI import settings, configure, InfoDialog
from grive_indicator.tools import getIcon, root_dir, ind, Config, config_file

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Start dbus
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

class GriveIndicator(dbus.service.Object):

    def __init__(self, bus, path, name):
        dbus.service.Object.__init__ (self, bus, path, name)
        self.running = False

    @dbus.service.method ("org.example.grive_indicator")
    def is_running (self):
        return self.running

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
        self.syncNow(None)
        GLib.timeout_add_seconds(60 * int(Config().getValue('time')), self.refresh)

    def syncDaemon(self):
        executor = futures.ThreadPoolExecutor(max_workers=1)
        self.future = executor.submit(self.refresh)

    def syncNow(self, widget):
        self.lastSync_item.set_label('Syncing...')
        folder = Config().getValue('folder')
        grive_cmd = ['grive']
        if not os.path.isfile(os.path.join(folder, '.grive')):
            # Run grive for the first time
            # On sequent runs grive remembers the selective setting.
            selective = Config().getValue('selective')
            if selective != '':
                grive_cmd.append('--dir "{}"'.format(selective))
        self.lastSync = re.split('T|\.', datetime.now().isoformat())[1]
        upload_speed = Config().getValue('upload_speed')
        if upload_speed != '':
            grive_cmd.append('--upload-speed {}'.format(upload_speed))
        download_speed = Config().getValue('download_speed')
        if download_speed != '':
            grive_cmd.append('--download-speed {}'.format(download_speed))
        try:
            logger.debug('Running: {}'.format(grive_cmd))
            subprocess.check_call(grive_cmd, cwd=folder)
        except CalledProcessError as e:
            response = UI.InfoDialog.main(parent=None, title='Error', label='Something went terribly wrong.')
            if response == Gtk.ResponseType.OK:
                logger.error('Error occurred running grive')
                Gtk.main_quit()
                exit(1)
        self.lastSync_item.set_label('Last sync at ' + self.lastSync)

    def openRemote(self, widget):
        subprocess.run(["xdg-open", "https://drive.google.com/"])

    def openLocal(self, widget):
        subprocess.run(["xdg-open", Config().getValue('folder')])

    def settings(self, widget):
        settings.main()

    def Quit(self, widget):
        if self.future.running():
            response = UI.InfoDialog.main(parent=None, title='Warning',
                                          label='Grive is currently syncing. Please wait a moment.')
            if response == Gtk.ResponseType.OK:
                logger.debug('Finishing sync.')
        Gtk.main_quit()

    @dbus.service.method("org.example.grive_indicator")
    def main(self):
        parser = argparse.ArgumentParser(description='Grive Indicator.')
        parser.add_argument('--folder', '-f', action='store')
        parser.add_argument('--selective', '-s', action='store')
        args = parser.parse_args()
        folder = args.folder
        selective = args.selective

        if not shutil.which('grive'):
            print('Missing grive executable in PATH.')
            exit(1)

        self.menu_setup()
        ind.set_menu(self.menu)
        if not os.path.exists(config_file):
            logger.debug('Missing config file %s.' % config_file)
            configure.main()
        else:
            self.syncDaemon()
        Gtk.main()

def main():
    bus = dbus.SessionBus ()
    request = bus.request_name ("org.example.grive_indicator", dbus.bus.NAME_FLAG_DO_NOT_QUEUE)
    if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
        app = GriveIndicator (bus, '/', "org.example.grive_indicator")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        app.main()
