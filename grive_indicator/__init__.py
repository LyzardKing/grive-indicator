#!/usr/bin/env python3

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
from grive_indicator import settings
from grive_indicator.tools import getIcon, GRIVEI_PATH, setValue, getValue, ind
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

LOCK = False

logging.basicConfig(format="%(levelname)s: %(message)s")


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
        if not shutil.which('zenity'):
            print('Missing zenity executable in PATH.')
            exit(1)
        try:
            with open("{}/.grive-indicator".format(os.environ['HOME']), 'r') as json_data:
                data = json.load(json_data)
                if data["style"] is None or data["time"] is None:
                    raise FileNotFoundError
        except FileNotFoundError:
            if not folder:
                logging.error("Folder needed. Usage: grive-indicator --folder <folder>")
                selective = subprocess.check_output(['zenity', '--forms',
                                                  '--text="Configuration file missing. Add the remote folder to sync(leave blank to sync all)"',
                                                  '--add-entry="Remote Folder (selective sync)"'])
                selective = selective.decode().strip()
                folder = subprocess.check_output(['zenity', '--title="Local Folder"', '--file-selection', '--directory'])
                folder = folder.decode().strip()
                if not os.path.isfile(os.path.join(folder, '.grive')):
                    result = subprocess.check_output(['zenity', '--question',
                                                      '--text="The folder is not currently registered with grive. Do you want to proceed?"'])
                    if result == b'':
                        # Authenticate with Google Drive
                        self.runAuth(folder)
            data = {"style": "dark", "time": 30,
                    "folder": folder,
                    "selective": selective}
            with open("{}/.grive-indicator".format(os.environ['HOME']), 'w+') as json_data:
                json.dump(data, json_data)

        self.menu_setup()
        ind.set_menu(self.menu)

        while not os.path.isfile(os.path.join(os.environ['HOME'], '.grive-indicator')) and\
              not os.path.isfile(folder, '.grive') and\
              not LOCK:
            sleep(3)
        self.syncDaemon()

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

    def runAuth(self, folder):
        LOCK = True
        thread = threading.Thread(target=self._runAuth, args=[folder])
        thread.start()
        self.lastSync_item.set_label('Initial Sync...')
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

    def syncDaemon(self):
        thread = threading.Thread(target=self.refresh)
        thread.daemon = True
        thread.start()

    def syncNow(self, _):
        self.lastSync_item.set_label('Syncing...')
        folder = getValue('folder')
        if not os.path.isfile(os.path.join(folder, '.grive')):
            # Run grive for the first time
            # On sequent runs grive remembers the selective setting.
            # TODO: How to change the selective settings
            selective = getValue('selective')
            if selective != '':
                grive_cmd = ['grive', '--dir "{}"'.format(selective)]
            else:
                grive_cmd = ['grive']
        self.lastSync = re.split('T|\.', datetime.now().isoformat())[1]
        subprocess.run(['killall', 'grive'])
        try:
            subprocess.check_call(['grive'], cwd=folder)
        except CalledProcessError as e:
            output = subprocess.check_output(['zenity', '--error', '--text="You need to Authenticate with Grive"'])
            if output == b'':
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
