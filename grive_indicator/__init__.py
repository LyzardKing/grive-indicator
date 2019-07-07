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


import argparse
import gi
import logging
import os
import re
import signal
import subprocess

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from concurrent import futures
from datetime import datetime
from gi.repository import Gtk, Gdk, Gio, GLib, Notify
from grive_indicator.UI import settings, configure
from grive_indicator.tools import ind, Config, config_file,\
    is_connected, runConfigure, show_notify, get_version

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class GriveIndicator(Gtk.Application):

    def __init__(self, cliArgs, *args, **kwargs):
        super().__init__(*args, application_id="com.github.lyzardking.grive_indicator",
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        if cliArgs.version:
            print(get_version())
            exit()
        self.folder = cliArgs.folder
        self.debug = cliArgs.debug

    def on_activate(self, *_):
        if not self.future.running():
            logger.debug("Already Running: Running sync")
            self.lastSync_item.set_label('Syncing...')
            self.syncNow(None)
        else:
            logger.debug("Sync already running")

    def do_startup(self):
        Gtk.Application.do_startup(self)
        try:
            self.nocsd = not Config().getBool('use_csd')
        except Exception as e:
            logger.error(e)
            self.nocsd = True

        self.menu_setup()
        ind.set_menu(self.menu)
        if self.folder:
            runConfigure(folder=self.folder)
        if not os.path.exists(config_file):
            logger.debug('Setting config file %s.' % config_file)
            configure.main(self.nocsd)
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
            self.lastSync_item.set_label('Syncing...')
            self.syncNow(None)
        GLib.timeout_add_seconds(60 * int(Config().getValue('time')), self.refresh)

    def syncDaemon(self):
        executor = futures.ThreadPoolExecutor(max_workers=1)
        self.future = executor.submit(self.refresh)

    def syncNow(self, widget):
        self.lastSync_item.set_label('Syncing...')
        folder = Config().getValue('folder')
        grive_cmd = ['grive']
        # grive_cmd = ['/snap/bin/grive-indicator.grive']
        upload_speed = Config().getValue('upload_speed')
        if upload_speed != "0":
            grive_cmd.append('--upload-speed {}'.format(upload_speed))
        download_speed = Config().getValue('download_speed')
        if download_speed != "0":
            grive_cmd.append('--download-speed {}'.format(download_speed))
        if self.debug:
            logger.setLevel('DEBUG')
            logger.debug('Running in debug mode')
            logger.debug('Emulate sync, then update label')
        try:
            logger.debug('Running: {}'.format(grive_cmd))
            result = subprocess.run(grive_cmd,
                                    cwd=folder,
                                    stderr=subprocess.STDOUT,
                                    stdout=subprocess.PIPE)
            notify = Config().getValue('show_notifications')
            if self.debug:
                for grive_out_line in str.splitlines(result.stdout.decode()):
                    logger.debug('Grive log: ' + grive_out_line)
                    if notify:
                        if grive_out_line.startswith('sync'):
                            show_notify(grive_out_line)
            logger.debug('Finished sync')
            self.lastSync = re.split('T|\.', datetime.now().isoformat())[1]
            self.lastSync_item.set_label('Last sync at ' + self.lastSync)
        except OSError:
            logger.error('Missing grive in PATH')
            pass
        except Exception as e:
            logger.error('Error occurred running grive. Skipping sync: %s' % e)
            pass

    def openRemote(self, widget):
        Gtk.show_uri_on_window(None, "https://drive.google.com", Gdk.CURRENT_TIME)

    def openLocal(self, widget):
        localFolder = "file://{}".format(Config().getValue('folder'))
        if os.getenv("SNAP") is not None:
            logger.debug("Opening {} in snap: xdg-open".format(localFolder))
            subprocess.call(["xdg-open", localFolder])
        else:
            logger.debug("Opening {}: show_uri_on_window".format(localFolder))
            Gtk.show_uri_on_window(None, localFolder, Gdk.CURRENT_TIME)
        # subprocess.call(["xdg-open", "file://{}".format(Config().getValue('folder'))])

    def settings(self, widget):
        settings.main(self.debug, self.nocsd)

    def Quit(self, widget=None):
        logger.debug("Closing...")
        if self.future.running():
            Notify.Notification.new('Grive is terminating a sync').show()
        Gtk.main_quit()


def main():
    # Glib steals the SIGINT handler and so, causes issue in the callback
    # https://bugzilla.gnome.org/show_bug.cgi?id=622084
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    parser = argparse.ArgumentParser(description='Grive Indicator.')
    parser.add_argument('--folder', '-f', action='store', help='Custom destination folder')
    parser.add_argument('--debug', action='store_true', help='Debug mode without grive')
    parser.add_argument('--version', action='store_true', help='Print the version and quit')
    # TODO: Add auth parameter
    args = parser.parse_args()

    app = GriveIndicator(args)
    app.connect("activate", app.on_activate)
    # app.connect("startup", app.do_startup)

    app.run()
