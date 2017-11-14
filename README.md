grive-indicator
===============
![Build Status](https://api.travis-ci.org/LyzardKing/grive-indicator.svg?branch=master)


Linux Gtk indicator to sync Google Drive via Grive
=======
A very simple and lightweight indicator applet to synchronize with Google Drive using grive.

Works with "selective sync". You can specify one folder to sync (only one). That is permanent and cannot be changed.

Prerequisites
===============

1. Install "grive", "python-appindicator"
2. If using for the first time, magic happens ;). (It will run grive -a, open a webpage and ask for the code, parsing the cli grive)

Installation
===============

"grive-indicator" at the moment can be started manually, or added to the startup applications via the menu.

Tests
===============
Successfully tested under: Ubuntu 16.10 (Mate)

ToDo
===============

1. Add sync based on inotifywait (e.g. using a command like: inotifywait -r -e modify,attrib,moved_to,moved_from,move_self,create,delete,delete_self "$HOME/Google Drive")

The icons are copyright © Sam Hewitt, from the Paper Icons theme, available under the terms of the CC-BY-SA-4.0 license.
