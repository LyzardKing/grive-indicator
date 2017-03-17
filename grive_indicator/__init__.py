#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
import argparse
import os
import shutil
import subprocess
import sys
import json
import site
import re
import threading
import logging
from time import sleep
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
from grive_indicator import settings
from grive_indicator import configure
from grive_indicator import UI
from grive_indicator.tools import getIcon, GRIVEI_PATH, setValue, getValue, ind


logger = logging.getLogger(__name__)


class GriveIndicator:

    def __init__(self):
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

        if not os.path.exists(os.path.join(os.environ['HOME'], '.grive-indicator')):
            # self.lastSync_item.set_label('Initial Sync...')
            configure.main()
        else:
            self.syncDaemon()

        # while not os.path.isfile(os.path.join(os.environ['HOME'], '.grive-indicator')):
        #     sleep(3)
        # self.syncDaemon()

    def menu_setup(self):
        self.menu = Gtk.Menu()

        self.lastSync_item = Gtk.MenuItem('Not Available')
        self.lastSync_item.set_sensitive(False)
        self.lastSync_item.show()

        self.syncNow_item = Gtk.MenuItem("Sync now")
        self.syncNow_item.connect("activate", self.syncNow)
        self.syncNow_item.show()

        self.seperator1_item = Gtk.SeparatorMenuItem()
        self.seperator1_item.show()

        self.Remote_item = Gtk.MenuItem("Open remote GDrive")
        self.Remote_item.connect("activate", self.openRemote)
        self.Remote_item.show()

        self.Local_item = Gtk.MenuItem("Open local GDrive")
        self.Local_item.connect("activate", self.openLocal)
        self.Local_item.show()

        self.Local_item = Gtk.MenuItem("Open Settings")
        self.Local_item.connect("activate", self.settings)
        self.Local_item.show()

        self.seperator3_item = Gtk.SeparatorMenuItem()
        self.seperator3_item.show()

        self.Quit_item = Gtk.MenuItem("Quit")
        self.Quit_item.connect("activate", self.Quit)
        self.Quit_item.show()

        self.menu.append(self.lastSync_item)
        self.menu.append(self.syncNow_item)
        self.menu.append(self.seperator1_item)
        self.menu.append(self.Remote_item)
        self.menu.append(self.Local_item)
        self.menu.append(self.seperator3_item)
        self.menu.append(self.Quit_item)

    def refresh(self):
        self.syncNow(None)
        GLib.timeout_add_seconds(60 * int(getValue('time')), self.refresh)

    def enableInotifywait(self):
        p = Process(target=notifyProcess, args=None)
        p.start()

    def syncDaemon(self):
        thread = threading.Thread(target=self.refresh)
        thread.daemon = True
        thread.start()

    def syncNow(self, _):
        self.lastSync_item.set_label('Syncing...')
        folder = getValue('folder')
        grive_cmd = ['grive', '--dry-run']
        if not os.path.isfile(os.path.join(folder, '.grive')):
            # Run grive for the first time
            # On sequent runs grive remembers the selective setting.
            # TODO: How to change the selective settings
            selective = getValue('selective')
            if selective != '':
                grive_cmd.append('--dir "{}"'.format(selective))
        self.lastSync = re.split('T|\.', datetime.now().isoformat())[1]
        subprocess.run(['killall', 'grive'])
        upload_speed = getValue('upload_speed')
        if upload_speed != '':
            grive_cmd.append('--upload-speed {}'.format(upload_speed))
        download_speed = getValue('download_speed')
        if download_speed != '':
            grive_cmd.append('--download-speed {}'.format(download_speed))
        try:
            logger.debug('Running: {}'.format(grive_cmd))
            subprocess.check_call(grive_cmd, cwd=folder)
        except CalledProcessError as e:
            response = UI.InfoDialog.main(parent=None, label='Something went terribly wrong.')
            if response == Gtk.ResponseType.OK:
                logger.error('Error occurred running grive')
                Gtk.main_quit()
                exit(1)
        self.lastSync_item.set_label('Last sync at ' + self.lastSync)

    def openRemote(self, _):
        subprocess.Popen(["xdg-open", "https://drive.google.com/"])

    def openLocal(self, _):
        subprocess.Popen(["xdg-open", getValue('folder')])

    def settings(self, _):
        settings.main()

    def Quit(self, _):
        subprocess.run(['killall', 'grive-sync'])
        Gtk.main_quit()

    def main(self):
        Gtk.main()


def main():
    indicator = GriveIndicator()
    indicator.main()
