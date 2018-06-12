from unittest import TestCase

from grive_indicator.tools import is_connected


class ToolsTest(TestCase):

    def test_internet_active(self):
        """Validate an active internet connection with the default settings"""

        # we want to use either local or system grive_indicator, but always local tests files
        result = is_connected()
        self.assertEqual(result, True)

    def test_internet_404(self):
        """Test a failing internet connection. Return a 404 error"""
        result = is_connected(url="https://httpstat.us/408")
        self.assertEqual(result, False)
