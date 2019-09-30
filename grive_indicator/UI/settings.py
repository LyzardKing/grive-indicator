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

import gi
import logging
import os
import re
import shutil
import site
import subprocess

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from contextlib import suppress
from xdg.BaseDirectory import xdg_config_home
from ..tools import getIcon, Config, ind, root_dir, autostart_file, griveignore_init

logger = logging.getLogger(__name__)


class SettingsWindow(Gtk.Window):
    def __init__(self, debug):
        Gtk.Window.__init__(self, title="Settings")
        self.set_icon_name("web-google-drive")

        self.debug = debug
        self.set_default_size(150, 100)
        self.set_border_width(18)

        self.grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.add(self.grid)

        conf = Config()
        label_timer = Gtk.Label("Sync timer (min)", xalign=1)
        self.timer_entry = Gtk.SpinButton()
        self.timer_entry.set_numeric(True)
        self.timer_entry.set_adjustment(Gtk.Adjustment(0, 0, 100, 1, 10, 0))
        self.timer_entry.set_value(int(conf.getValue("time")))

        label_theme = Gtk.Label("Dark Theme", xalign=1)
        theme_swith = Gtk.Switch(halign=Gtk.Align.START)
        # TODO Fix for custom themes
        theme_swith.set_active(conf.getBool("dark"))
        theme_swith.connect("notify::active", self.on_dark_theme_activate)

        label_startup = Gtk.Label("Enable on Startup", xalign=1)
        startup_swith = Gtk.Switch(halign=Gtk.Align.START)
        startup_swith.set_active(autostart_file.is_file())
        startup_swith.connect("notify::active", self.on_startup_active)

        label_notification = Gtk.Label("Enable Notifications", xalign=1)
        notification_switch = Gtk.Switch(halign=Gtk.Align.START)
        notification_switch.set_active(bool(conf.getValue("show_notifications")))
        notification_switch.connect("notify::active", self.on_notification_activate)

        label_new_rev = Gtk.Label("Enable revisions", xalign=1)
        new_rev_switch = Gtk.Switch(halign=Gtk.Align.START)
        new_rev_switch.set_active(conf.getBool("revisions"))
        new_rev_switch.connect("notify::active", self.on_revisions_activate)

        label_custom_options = Gtk.Label("Custom options", xalign=1)
        self.custom_options = Gtk.Entry()

        label_up_speed = Gtk.Label("Limit Upload Speed", xalign=1)
        self.upload_speed = Gtk.SpinButton()
        self.upload_speed.set_numeric(True)
        self.upload_speed.set_adjustment(Gtk.Adjustment(0, 0, 100, 1, 10, 0))
        self.upload_speed.set_value(int(conf.getValue("upload_speed")))

        label_down_speed = Gtk.Label("Limit Download Speed", xalign=1)
        self.download_speed = Gtk.SpinButton()
        self.download_speed.set_numeric(True)
        self.download_speed.set_adjustment(Gtk.Adjustment(0, 0, 100, 1, 10, 0))
        self.download_speed.set_value(int(conf.getValue("download_speed")))

        edit_ignore = Gtk.Button("Update .griveignore")
        edit_ignore.connect("clicked", self.open_griveignore)

        confirm_button = Gtk.Button("Ok")
        confirm_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        confirm_button.connect("clicked", self.confirmSettings)

        cancel_button = Gtk.Button("Cancel")
        cancel_button.get_style_context().add_class(Gtk.STYLE_CLASS_DESTRUCTIVE_ACTION)
        cancel_button.connect("clicked", self.close_window)

        self.grid.add(label_timer)
        self.grid.attach(self.timer_entry, 1, 0, 2, 1)
        self.grid.attach_next_to(
            label_theme, label_timer, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(theme_swith, label_theme, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(
            label_startup, label_theme, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            startup_swith, label_startup, Gtk.PositionType.RIGHT, 2, 1
        )
        self.grid.attach_next_to(
            label_notification, label_startup, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            notification_switch, label_notification, Gtk.PositionType.RIGHT, 2, 1
        )
        self.grid.attach_next_to(
            label_new_rev, label_notification, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            new_rev_switch, label_new_rev, Gtk.PositionType.RIGHT, 2, 1
        )
        self.grid.attach_next_to(
            label_custom_options, label_new_rev, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            self.custom_options, label_custom_options, Gtk.PositionType.RIGHT, 2, 1
        )
        self.grid.attach_next_to(
            label_up_speed, label_custom_options, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            self.upload_speed, label_up_speed, Gtk.PositionType.RIGHT, 2, 1
        )
        self.grid.attach_next_to(
            label_down_speed, label_up_speed, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            self.download_speed, label_down_speed, Gtk.PositionType.RIGHT, 2, 1
        )
        self.grid.attach_next_to(
            edit_ignore, self.download_speed, Gtk.PositionType.BOTTOM, 1, 1
        )

        self.grid.attach_next_to(
            confirm_button, edit_ignore, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            cancel_button, confirm_button, Gtk.PositionType.LEFT, 1, 1
        )

    def open_griveignore(self, gparam):
        griveignore = Path(Config().getValue("folder") / ".griveignore")
        if not griveignore.is_file():
            with open(griveignore, "w") as griveignore_file:
                griveignore_file.write(griveignore_init)
        try:
            # Gtk.show_uri(None,
            #              "file://{}".format(griveignore),
            #              Gdk.CURRENT_TIME)
            subprocess.call(["xdg-open", "file://{}".format(griveignore)])
        except Exception as e:
            logger.error("Accessing griveignore file: %s" % e)

    def on_log_activate(self, switch, gparam):
        Config().setValue("log", switch.get_active())

    def on_notification_activate(self, switch, gparam):
        if switch.get_active():
            response = Gtk.MessageDialog(
                self,
                0,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                "Could cause issues when syncing a large number of files."
                "Do you want to enable it?",
            ).run()
            if response == Gtk.ResponseType.NO:
                Config().setValue("show_notifications", False)
                switch.set_active(False)
            if response == Gtk.ResponseType.YES:
                Config().setValue("show_notifications", True)
            response.destroy()
        else:
            Config().setValue("show_notifications", False)

    def on_dark_theme_activate(self, switch, gparam):
        if switch.get_active():
            setDarkTheme()
        else:
            setLightTheme()

    def on_startup_active(self, switch, gparam):
        enableStartup(switch.get_active())

    def on_revisions_activate(self, switch, gparam):
        self.revisions = switch.get_active()
        if switch.get_active():
            logger.info("Add revision support")
        else:
            logger.info("Remove revision support")
        Config().setValue("revisions", str(switch.get_active()).lower())

    def close_window(self, widget):
        self.destroy()

    def confirmSettings(self, widget):
        # Do not save in debug mode
        if self.debug:
            self.destroy()
            return

        logger.debug(
            "Set timer, up, down to %s, %s, %s"
            % (
                self.timer_entry.get_text(),
                self.upload_speed.get_text(),
                self.download_speed.get_text(),
            )
        )
        with suppress(ValueError):
            setInterval(self.timer_entry.get_text())
        with suppress(ValueError):
            setUploadSpeed(self.upload_speed.get_text())
        with suppress(ValueError):
            setDownloadSpeed(self.download_speed.get_text())
        with suppress(ValueError):
            setCustomOptions(self.custom_options.get_text())
        self.destroy()


def setDownloadSpeed(value):
    if value is not None and value != Config().getValue("download_speed"):
        Config().setValue("download_speed", value)


def setUploadSpeed(value):
    if value is not None and value != Config().getValue("upload_speed"):
        Config().setValue("upload_speed", value)


def setInterval(value):
    if value is not None and value != Config().getValue("time"):
        Config().setValue("time", value)


def setCustomOptions(value):
    if value is not None and value != Config().getValue("custom_options"):
        Config().setValue("custom_options", value)


def enableStartup(is_active):
    if is_active:
        logger.debug("Enable autostart")
        if os.getenv("SNAP") is not None:
            logger.error("Running in confined snap. Autostart manually")
            return
        if not autostart_file.is_file():
            Path.mkdir(Path(xdg_config_home / "autostart"), parents=True, exist_ok=True)
            shutil.copyfile(
                src=Path(root_dir / "data" / "grive-indicator.desktop"),
                dst=autostart_file,
            )
            with open(autostart_file, "r") as f:
                txt = f.read()
                if root_dir.parent in site.getsitepackages():
                    txt = re.sub(r"root_dir/", "", txt)
                else:
                    # Not an install, we keep the local version you're using
                    txt = re.sub(
                        r"root_dir/",
                        Path(root_dir.parent / bin / ""),
                        txt,
                    )
            with open(autostart_file, "w") as f:
                f.write(txt)
    else:
        logger.debug("Disable autostart")
        if autostart_file.is_file():
            os.remove(autostart_file)


def setDarkTheme():
    Config().setValue("dark", "true")
    ind.set_icon_full(Path(root_dir / "data" / getIcon()), "grive-indicator-dark")


def setLightTheme():
    Config().setValue("dark", "false")
    ind.set_icon_full(
        Path(root_dir / "data" / getIcon()), "grive-indicator-light"
    )


def main(debug):
    window = SettingsWindow(debug)
    window.show_all()
