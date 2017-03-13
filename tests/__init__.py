#!/usr/bin/env python3

import os
import pep8
import grive_indicator
from pathlib import Path
from grive_indicator import GRIVEI_PATH
import unittest


class CodeCheck(unittest.TestCase):
    def test_pep8(self):
        """Proceed a pep8 checking

        Note that we have a .pep8 config file for maximum line length tweak
        and excluding the virtualenv dir."""
        config_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        pep8style = pep8.StyleGuide(config_file=os.path.join(config_folder, '.pep8'))

        # we want to use either local or system umake, but always local tests files
        dir_grive_indicator = os.path.dirname(os.path.join(config_folder, 'grive_indicator'))
        results = pep8style.check_files([dir_grive_indicator, os.path.join(config_folder, "bin")])
        self.assertEqual(results.get_statistics(), [])

if __name__ == '__main__':
    unittest.main()
