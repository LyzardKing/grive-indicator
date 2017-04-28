#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gi
import re
import shutil
import site
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from contextlib import suppress
import logging
from ..tools import getIcon, Config, ind, root_dir, autostart_file, griveignore_init
from ..UI import CSDWindow

logger = logging.getLogger(__name__)


class SettingsWindow(CSDWindow):

    def __init__(self):
        super().__init__(title='Settings')

        conf = Config()
        label_timer = Gtk.Label("Sync timer")
        self.timer_entry = Gtk.Entry()
        self.timer_entry.set_text(conf.getValue('time'))

        label_theme = Gtk.Label("Dark Theme")
        theme_swith = Gtk.Switch()
        # TODO Fix for custom themes
        theme_swith.set_active(Config().getValue('style') == 'dark')
        theme_swith.connect('notify::active', self.on_dark_theme_activate)

        label_startup = Gtk.Label("Enable on Startup")
        startup_swith = Gtk.Switch()
        startup_swith.set_active(os.path.isfile(autostart_file))
        startup_swith.connect('notify::active', self.on_startup_active)

        label_notification = Gtk.Label("Enable Notifications")
        notification_switch = Gtk.Switch()
        notification_switch.set_active(conf.config['DEFAULT'].getboolean('show_notifications'))
        notification_switch.connect('notify::active', self.on_notification_activate)

        label_up_speed = Gtk.Label("Limit Upload Speed")
        self.upload_speed = Gtk.Entry()
        tmp = conf.getValue('upload_speed')
        self.upload_speed.set_text(tmp if tmp is not None else '')

        label_down_speed = Gtk.Label("Limit Download Speed")
        self.download_speed = Gtk.Entry()
        tmp = conf.getValue('download_speed')
        self.download_speed.set_text(tmp if tmp is not None else '')

        edit_ignore = Gtk.Button('Update .griveignore')
        edit_ignore.connect('clicked', self.open_griveignore)

        confirm_button = Gtk.Button('Ok')
        confirm_button.connect('clicked',
                               self.confirmSettings)

        self.grid.add(label_timer)
        self.grid.attach(self.timer_entry, 1, 0, 2, 1)
        self.grid.attach_next_to(label_theme, label_timer, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(theme_swith, label_theme, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(label_startup, label_theme, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(startup_swith, label_startup, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(label_notification, label_startup, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(notification_switch, label_notification, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(label_up_speed, label_notification, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.upload_speed, label_up_speed, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(label_down_speed, label_up_speed, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.download_speed, label_down_speed, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(edit_ignore, self.download_speed, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(confirm_button, edit_ignore, Gtk.PositionType.BOTTOM, 1, 1)

    def open_griveignore(self, gparam):
        griveignore = os.path.join(Config().getValue('folder'), '.griveignore')
        if not os.path.isfile(griveignore):
            with open(griveignore, 'w') as griveignore_file:
                griveignore_file.write(griveignore_init)
        try:
            Gtk.show_uri(None,
                         "file://{}".format(griveignore),
                         Gdk.CURRENT_TIME)
        except Exception as e:
            logger.error('Accessing griveignore file: %s' % e)

    def on_log_activate(self, switch, gparam):
        Config().setValue('log', switch.get_active())

    def on_notification_activate(self, switch, gparam):
        Config().setValue('show_notifications', str(switch.get_active()))

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
