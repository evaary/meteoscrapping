import unittest

from app.tests.checker_tests import CheckerTester
from app.tests.meteociel_tests import (Meteociel_DailyTester,
                                       Meteociel_MonthlyTester)
from app.tests.ogimet_tests import Ogimet_MonthlyTester
from app.tests.wunderground_tests import Wunderground_MonthlyTester

if __name__ == "__main__":
    unittest.main()