#!/usr/bin/env python3

import os
import pep8
from flake8.api import legacy as flake8
import unittest

config_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class CodeCheck(unittest.TestCase):

    def test_pep8(self):
        """Proceed a pep8 checking

        Note that we have a .pep8 config file for maximum line length tweak
        and excluding the virtualenv dir."""
        pep8style = pep8.StyleGuide(config_file=os.path.join(config_folder, '.pep8'))

        # we want to use either local or system umake, but always local tests files
        dir_grive_indicator = os.path.dirname(os.path.join(config_folder, 'drive_indicator'))
        results = pep8style.check_files([dir_grive_indicator, os.path.join(config_folder, "bin")])
        self.assertEqual(results.get_statistics(), [])

    def test_flake8(self):
        """Proceed a flake8 checking

        Pass the options directly until the api can read .flake8."""
        style_guide = flake8.get_style_guide(ignore=['E402'],
                                             max_line_length=120,
                                             exclude=['build/'])

        # we want to use either local or system umake, but always local tests files
        dir_grive_indicator = os.path.dirname(os.path.join(config_folder, 'drive_indicator'))
        results = style_guide.check_files([dir_grive_indicator, os.path.join(config_folder, "bin")])
        self.assertEqual(results.get_statistics('E'), [])


if __name__ == '__main__':
    unittest.main()
