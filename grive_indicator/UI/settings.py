#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gi
import re
import shutil
import site
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from contextlib import suppress
import logging
import subprocess
from grive_indicator.tools import getIcon, Config, ind, root_dir, autostart_file

logger = logging.getLogger(__name__)


class SettingsWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Settings")

        self.set_border_width(6)

        grid = Gtk.Grid()
        self.add(grid)
        conf = Config()
        label_timer = Gtk.Label("Sync timer")
        self.timer_entry = Gtk.Entry()
        self.timer_entry.set_text(conf.getValue('time'))

        label_theme = Gtk.Label("Dark Theme")
        theme_swith = Gtk.Switch()
        # TODO Fix for custom themes
        theme_swith.set_active(Config().getValue('style') == 'dark')
        theme_swith.connect('notify::active', self.on_dark_theme_activate)

        label_startup = Gtk.Label("Enable  on Startup")
        startup_swith = Gtk.Switch()
        startup_swith.set_active(os.path.isfile(autostart_file))
        startup_swith.connect('notify::active', self.on_startup_active)

        label_up_speed = Gtk.Label("Limit Upload Speed")
        self.upload_speed = Gtk.Entry()
        tmp = conf.getValue('upload_speed')
        self.upload_speed.set_text(tmp if tmp is not None else '')

        label_down_speed = Gtk.Label("Limit Download Speed")
        self.download_speed = Gtk.Entry()
        tmp = conf.getValue('download_speed')
        self.download_speed.set_text(tmp if tmp is not None else '')

        confirm_button = Gtk.Button('Ok')
        confirm_button.connect('clicked',
                               self.confirmSettings)

        grid.add(label_timer)
        grid.attach(self.timer_entry, 1, 0, 2, 1)
        grid.attach_next_to(label_theme, label_timer, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(theme_swith, label_theme, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(label_startup, label_theme, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(startup_swith, label_startup, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(label_up_speed, label_startup, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.upload_speed, label_up_speed, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(label_down_speed, label_up_speed, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.download_speed, label_down_speed, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach_next_to(confirm_button, self.download_speed, Gtk.PositionType.BOTTOM, 1, 1)

    def on_dark_theme_activate(self, switch, gparam):
        if switch.get_active():
            setDarkTheme()
        else:
            setLightTheme()

    def on_startup_active(self, switch, gparam):
        enableStartup(switch.get_active())

    def confirmSettings(self, widget):
        logger.debug('Set timer, up, down to %s, %s, %s' % (self.timer_entry.get_text(),
                                                            self.upload_speed.get_text(),
                                                            self.download_speed.get_text()))
        with suppress(ValueError):
            setInterval(self.timer_entry.get_text())
        with suppress(ValueError):
            setUploadSpeed(self.upload_speed.get_text())
        with suppress(ValueError):
            setDownloadSpeed(self.download_speed.get_text())
        self.destroy()


def setDownloadSpeed(value):
    if value is not None and value != Config().getValue('download_speed'):
        Config().setValue('download_speed', value)


def setUploadSpeed(value):
    if value is not None and value != Config().getValue('upload_speed'):
        Config().setValue('upload_speed', value)


def setInterval(value):
    if value is not None and value != Config().getValue('time'):
        Config().setValue("time", value)


def enableStartup(is_active):
    if is_active:
        if not os.path.isfile(autostart_file):
            shutil.copyfile(src=os.path.join(root_dir, "data", 'grive-indicator.desktop'),
                            dst=os.path.join(os.path.expanduser('~'), '.config',
                                             'autostart', 'grive-indicator.desktop'))
            with open(os.path.join(os.path.expanduser('~'), '.config', 'autostart',
                                   'grive-indicator.desktop'), 'r') as f:
                txt = f.read()
                print(root_dir)
                if os.path.dirname(root_dir) in site.getsitepackages():
                    txt = re.sub(r"root_dir/", '', txt)
                else:
                    txt = re.sub(r"root_dir/", '{}/'.format(os.path.join(os.path.dirname(root_dir), 'bin')), txt)
            with open(os.path.join(os.path.expanduser('~'), '.config', 'autostart',
                                   'grive-indicator.desktop'), 'w') as f:
                f.write(txt)
    else:
        if os.path.exists(autostart_file):
            os.remove(autostart_file)


def setDarkTheme():
    Config().setValue("style", "dark")

    ind.set_icon_full(os.path.join(root_dir, "data", getIcon()), "grive-indicator-dark")


def setLightTheme():
    Config().setValue("style", "light")
    ind.set_icon_full(os.path.join(root_dir, "data", getIcon()), "grive-indicator-light")


def main():
    window = SettingsWindow()
    window.show_all()
