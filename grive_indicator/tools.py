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


import configparser
import gi
import logging
import os
import re
import requests
import shutil
import subprocess
import sys

gi.require_version("AppIndicator3", "0.1")
gi.require_version("Gio", "2.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")

from contextlib import suppress
from gi.repository import AppIndicator3
from gi.repository import Gtk, Notify, GdkPixbuf, Gdk
from pathlib import Path
from xdg.BaseDirectory import xdg_config_home

root_dir = Path(__file__).resolve().parent
root_data = Path(root_dir / "data")
autostart_file = Path(Path(xdg_config_home) / "autostart/grive-indicator.desktop")
config_file = Path(Path(xdg_config_home) / "grive_indicator.conf")
log_file = Path(Path(xdg_config_home) / "grive_indicator.grive.log")

logger = logging.getLogger(__name__)
Notify.init(__name__)
griveignore_init = (
    "# Set rules For selective sync.\n"
    "# Check the man page or\n"
    "# https://github.com/vitalif/grive2#griveignore\n"
)


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def getValue(self, key):
        try:
            return self.config["DEFAULT"][key]
        except KeyError:
            return None

    def getBool(self, key):
        with suppress(KeyError):
            tmp = self.config["DEFAULT"][key]
            if tmp.lower() == "false":
                return False
            else:
                return True

    def setValue(self, key, value):
        logger.debug("Set config {} to {}".format(key, value))
        self.config["DEFAULT"][key] = value
        with open(config_file, "w") as configfile:
            self.config.write(configfile)
        notification = Notify.Notification.new(
            "{} set to {}.".format(key.capitalize(), value)
        )
        notification.set_icon_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file(getAlertIcon())
        )
        notification.show()


def is_connected(url="https://drive.google.com/", timeout=10):
    try:
        r = requests.get(url=url, timeout=timeout)
        r.raise_for_status()
        return True
    except requests.HTTPError as e:
        logger.error("HTTP error {0}.".format(e.response.status_code))
    except requests.ConnectionError:
        logger.error("No internet connection available.")
    return False


def runConfigure(folder, selective=None):
    if config_file.is_file():
        logger.info("A config file exists. Override? Y/n")
        if input().lower() != "y":
            return
    _runConfigure(folder, selective)
    if not Path(folder / ".grive").is_file():
        dialog = Gtk.MessageDialog(
            None,
            0,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.YES_NO,
            "The folder is not currently registered with grive",
        )
        dialog.format_secondary_text("Do you want to proceed?")
        dialog.run()

        if dialog == Gtk.ResponseType.YES:
            logger.debug("Confirm auth")
            # Authenticate with Google Drive
            runAuth(folder)


def _runConfigure(folder, selective=None):
    logger.debug("Saving configurations: folder:%s selective:%s" % (folder, selective))
    shutil.copy(Path(root_data / "grive_indicator.conf"), config_file)
    with open((folder / ".griveignore"), "w") as griveignore:
        griveignore.write(selective)
    conf = Config()
    conf.setValue("folder", folder)


def runAuth(folder):
    _runAuth(folder)


def _runAuth(folder):
    txt = ""
    auth = subprocess.Popen(
        ["grive", "-a", "--dry-run"],
        shell=False,
        cwd=folder,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    for line in iter(auth.stdout.readline, ""):
        txt += line.decode()
        if "Please input the authentication code" in txt:
            break
    url = re.search("https.*googleusercontent.com", txt).group(0)
    # Gtk.show_uri_on_window(None, url, Gdk.CURRENT_TIME)
    subprocess.call(["xdg-open", url])
    dialogWindow = Gtk.MessageDialog(
        None,
        0,
        Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.OK_CANCEL,
        "Insert the authentication code",
    )
    entry = Gtk.Entry()
    dialogWindow.get_content_area().pack_end(entry, False, False, 0)

    dialogWindow.show_all()
    response = dialogWindow.run()
    auth_response = entry.get_text()
    dialogWindow.destroy()
    if (response == Gtk.ResponseType.OK) and (auth_response != ""):
        logger.debug(auth_response)
        auth.stdin.write(auth_response.encode())
        auth.stdin.flush()
    else:
        return None


def getAlertIcon():
    return Path(root_dir / "data" / "drive-dark.svg")


def getIcon():
    try:
        dark = Config().getValue("dark")
    except Exception as e:
        logger.error(e)
        dark = "true"
    style = "dark" if dark == "true" else "light"
    icon_name = "drive-" + style + ".svg"
    icon = Path(root_dir / "data" / icon_name)
    return icon


def show_notify(line):
    key = line.split('"')[2]
    value = line.split('"')[1]
    notification = Notify.Notification.new("{} {}".format(key.capitalize(), value))
    notification.set_icon_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(getAlertIcon()))
    notification.show()


def openRemote(widget):
    Gtk.show_uri_on_window(None, "https://drive.google.com", Gdk.CURRENT_TIME)


def openLocal(widget):
    localFolder = "file://{}".format(Config().getValue("folder"))
    if os.getenv("SNAP") is not None:
        logger.debug("Opening {} in snap: xdg-open".format(localFolder))
        subprocess.call(["xdg-open", localFolder])
    else:
        logger.debug("Opening {}: show_uri_on_window".format(localFolder))
        Gtk.show_uri_on_window(None, localFolder, Gdk.CURRENT_TIME)
    # subprocess.call(["xdg-open", "file://{}".format(Config().getValue('folder'))])


def get_version():
    """Get version depending if on dev or released version"""
    version_file = Path(Path(__file__).resolve().parent / "version")
    version = open(version_file, "r", encoding="utf-8").read().strip()
    if os.getenv("SNAP_REVISION"):
        snap_appendix = ""
        snap_rev = os.getenv("SNAP_REVISION")
        if snap_rev:
            snap_appendix = "+snap{}".format(snap_rev)
        return version + snap_appendix
    import subprocess

    try:
        # use git describe to get a revision ref if running from a branch. Will append dirty if local changes
        version = (
            subprocess.check_output(["git", "describe", "--tags", "--dirty"])
            .decode("utf-8")
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        version += "+unknown"
    return version


ind = AppIndicator3.Indicator.new(
    "Grive Indicator",
    str(getIcon()),
    AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
)
ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
ind.set_attention_icon_full("indicator-messages-new", "Message attention icon")
