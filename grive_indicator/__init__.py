#!/usr/bin/env python3

import gi
import argparse
import os
import shutil
import subprocess
import sys
import json
import re
import threading
import logging

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

GRIVEI_PATH = os.path.abspath(os.path.join(str(Path(__file__).parents[0])))

logging.basicConfig(format="%(levelname)s: %(message)s")


class GriveIndicator:

    def __init__(self):
        parser = argparse.ArgumentParser(description='Grive Indicator.')
        parser.add_argument('--folder', '-f', action='store')
        parser.add_argument('--selective', '-s', action='store')
        args = parser.parse_args()

        if not shutil.which('grive'):
            print('Missing grive executable in PATH')
            exit(1)
        try:
            with open("{}/.grive-indicator".format(os.environ['HOME']), 'r') as json_data:
                data = json.load(json_data)
                if data["style"] is None or data["time"] is None:
                    raise FileNotFoundError
        except:
            if not args.folder:
                logging.error("Folder needed. Usage: grive-indicator --folder <folder>")
                exit(1)
            selective = args.selective if (args.selective is not None) else ''
            data = {"style": "dark", "time": 30,
                    "folder": args.folder,
                    "selective": selective}
            with open("{}/.grive-indicator".format(os.environ['HOME']), 'w+') as json_data:
                json.dump(data, json_data)
        self.autostart_file = os.path.join(os.path.expanduser('~'), '.config', 'autostart', 'grive-indicator.desktop')
        self.ind = AppIndicator3.Indicator.new("Grive Indicator", self.getIcon(),
                                               AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.menu_setup()
        self.ind.set_menu(self.menu)

        thread = threading.Thread(target=self.refresh)
        thread.daemon = True
        thread.start()

    def menu_setup(self):
        self.menu = Gtk.Menu()

        self.infoGrive_item = Gtk.MenuItem("Starting Grive")
        self.infoGrive_item.set_sensitive(False)
        self.infoGrive_item.show()

        self.lastSync_item = Gtk.MenuItem('Not Available')
        self.lastSync_item.set_sensitive(False)
        self.lastSync_item.show()

        self.setInterval_item = Gtk.MenuItem("Change sync interval")
        self.setInterval_item.connect("activate", self.setInterval)
        self.setInterval_item.show()

        self.onStartup_item = Gtk.CheckMenuItem('Enable on Startup')
        self.onStartup_item.set_active(os.path.isfile(self.autostart_file))
        self.onStartup_item.connect("activate", self.enableStartup)
        self.onStartup_item.show()

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

        self.seperator2_item = Gtk.SeparatorMenuItem()
        self.seperator2_item.show()

        self.DarkTheme_item = Gtk.MenuItem("Use dark theme icon")
        self.DarkTheme_item.connect("activate", self.setDarkTheme)
        self.DarkTheme_item.show()

        self.LightTheme_item = Gtk.MenuItem("Use light theme icon")
        self.LightTheme_item.connect("activate", self.setLightTheme)
        self.LightTheme_item.show()

        self.seperator3_item = Gtk.SeparatorMenuItem()
        self.seperator3_item.show()

        self.Quit_item = Gtk.MenuItem("Quit")
        self.Quit_item.connect("activate", self.Quit)
        self.Quit_item.show()

        self.menu.append(self.infoGrive_item)
        self.menu.append(self.lastSync_item)
        self.menu.append(self.setInterval_item)
        self.menu.append(self.syncNow_item)
        self.menu.append(self.seperator1_item)
        self.menu.append(self.Remote_item)
        self.menu.append(self.Local_item)
        self.menu.append(self.seperator2_item)
        self.menu.append(self.DarkTheme_item)
        self.menu.append(self.LightTheme_item)
        self.menu.append(self.onStartup_item)
        self.menu.append(self.seperator3_item)
        self.menu.append(self.Quit_item)

    def infoGrive(self):
        time = self.getValue('time')
        self.infoGrive_item.set_label("Grive sync every {} min".format(time))

    def refresh(self):
        self.syncNow(None)
        self.infoGrive()
        GLib.timeout_add_seconds(60 * int(self.getValue('time')), self.refresh)

    def enableInotifywait(self):
        p = Process(target=notifyProcess, args=None)
        p.start()

    def enableStartup(self, _):
        if self.onStartup_item.get_active():
            if not os.path.isfile(self.autostart_file):
                shutil.copyfile(src=os.path.join(GRIVEI_PATH, "data", 'grive-indicator.desktop'),
                                dst=os.path.join(os.path.expanduser('~'), '.config',
                                                 'autostart', 'grive-indicator.desktop'))
                with open(os.path.join(os.path.expanduser('~'), '.config', 'autostart',
                                       'grive-indicator.desktop'), 'r') as f:
                    txt = f.read()
                    txt = re.sub(r"GRIVEI_PATH", GRIVEI_PATH, txt)
                with open(os.path.join(os.path.expanduser('~'), '.config', 'autostart',
                                       'grive-indicator.desktop'), 'w') as f:
                    f.write(txt)
        else:
            if os.path.exists(self.autostart_file):
                os.remove(self.autostart_file)

    def syncNow(self, _):
        self.lastSync_item.set_label('Syncing...')
        folder = self.getValue('folder')
        if not os.path.isfile(os.path.join(folder, '.grive')):
            # Run grive for the first time
            # On sequent runs grive remembers the selective setting.
            # TODO: How to change the selective settings
            selective = self.getValue('selective')
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

    def getValue(self, key):
        with open("{}/.grive-indicator".format(os.environ['HOME']), 'r') as json_data:
            data = json.load(json_data)
        return data[key]

    def setValue(self, key, value):
        with open("{}/.grive-indicator".format(os.environ['HOME']), 'r') as json_data:
            data = json.load(json_data)
        with open("{}/.grive-indicator".format(os.environ['HOME']), 'w') as json_data:
            data[key] = value
            json.dump(data, json_data)
        subprocess.Popen(['notify-send', '{} set to {}.'.format(key.capitalize(), value),
                          '--icon={}/drive-dark.png'.format(os.path.abspath(os.path.join(GRIVEI_PATH, "data")))])

    def setDarkTheme(self, _):
        self.setValue("style", "dark")
        self.ind.set_icon_full(os.path.join(GRIVEI_PATH, "data", self.getIcon()), "grive-indicator-dark")

    def setLightTheme(self, _):
        self.setValue("style", "light")
        self.ind.set_icon_full(os.path.join(GRIVEI_PATH, "data", self.getIcon()), "grive-indicator-light")

    # TODO: remove zenity and set full preferences page
    def setInterval(self, _):
        out = subprocess.check_output(['zenity', '--scale', '--title="Grive sync interval"',
                                      '--min-value=1', '--max-value=180', '--value=1', '--step=1']).decode().strip()
        if out:
            self.setValue("time", out)
            self.infoGrive()

    def openRemote(self, _):
        subprocess.Popen(["xdg-open", "https://drive.google.com/"])

    def openLocal(self, _):
        subprocess.Popen(["xdg-open", self.getValue('folder')])

    # Build path for known icons, else return string
    # Use to set custom icons
    def getIcon(self):
        style = self.getValue('style')
        if style == 'light' or style == 'dark':
            return os.path.join(GRIVEI_PATH, "data", 'drive-' + style + '.png')
        else:
            return style

    def Quit(self, _):
        subprocess.run(['killall', 'grive-sync'])
        Gtk.main_quit()

    def main(self):
        Gtk.main()


#if __name__ == "__main__":
def main():
    indicator = GriveIndicator()
    indicator.main()
