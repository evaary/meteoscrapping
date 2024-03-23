import unittest

from app.tests.ucf_checker_tests import UCFCheckerTester
from app.tests.ucs_tests import UCsTester
from app.tests.tps_tests import TPsTester
from app.tests.meteociel_tests import (MeteocielDailyTester,
                                       MeteocielHourlyTester)
from app.tests.wunderground_tests import WundergroundDailyTester
from app.tests.ogimet_tests import OgimetDailyTester

if __name__ == "__main__":
    unittest.main()
