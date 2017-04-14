#!/usr/bin/env python3

import os
import pep8
import grive_indicator
from pathlib import Path
from grive_indicator import root_dir
import unittest
from unittest import mock
import requests
from requests.exceptions import HTTPError
import pexpect
from .tools import EXEC, spawn_process, check_and_kill_process


class TestInternetFail(unittest.TestCase):

    def test_no_internet(self):
        # TODO: Find a proper way to mock the connection
        return
        """Check that we fail gracefully if there is no internet."""
        config_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        with mock.patch.object(grive_indicator.tools, 'is_connected', return_value=False):
            child = spawn_process(EXEC)
            check_and_kill_process(EXEC, wait_before=10, send_sigkill=False)
            child.expect('ERROR: No internet connection available.', child.before)


if __name__ == '__main__':
    unittest.main()
