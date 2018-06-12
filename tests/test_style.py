import sys
import pyflakes
from pyflakes import api
from unittest import TestCase
from tests import folders


class StyleCheck(TestCase):

    def test_pyflakes(self):
        """Proceed a pyflakes checking"""

        # we want to use either local or system grive_indicator, but always local tests files
        reporter = pyflakes.reporter.Reporter(sys.stdout, sys.stderr)
        results = api.checkRecursive(paths=folders, reporter=reporter)
        self.assertEqual(results, 0)
