from unittest import TestCase

from app.ucs.UCFChecker import UCFChecker
from app.ucs.ucf_checker_exceptions import (DateFieldException,
                                            DaysDateException,
                                            MonthsDateException,
                                            NoSuchDateFieldException,
                                            UnavailableScrapperException,
                                            WaitingException,
                                            NoConfigFoundException,
                                            NotAJsonFileException,
                                            NotAJsonObjectException,
                                            NotAJsonListException,
                                            EmptyConfigFileException,
                                            ScrapperUCException,
                                            CommonStrFieldException,
                                            SpecificStrFieldException,
                                            YearsDateException)


class UCFCheckerTester(TestCase):
    
    BASE_PATH = "./app/tests/ucfs"

    def test_nominal_case(self):
        try:
            UCFChecker.check(f"{self.BASE_PATH}/correct.json")
        except Exception:
            self.fail("UCFCheckerTester : le cas nominal ne fonctionne pas")

    def test_broken_configs(self):
        with self.assertRaises(NoConfigFoundException):
            UCFChecker.check(f"bouh")

        with self.assertRaises(NotAJsonFileException):
            UCFChecker.check(f"{self.BASE_PATH}/empty.json")

        with self.assertRaises(NotAJsonFileException):
            UCFChecker.check(f"{self.BASE_PATH}/malformed.json")

    def test_structure_errors_configs(self):
        with self.assertRaises(NotAJsonObjectException):
            UCFChecker.check(f"{self.BASE_PATH}/wrong_config.json")

        with self.assertRaises(NotAJsonObjectException):
            UCFChecker.check(f"{self.BASE_PATH}/invalid_parameters.json")

        with self.assertRaises(ScrapperUCException):
            UCFChecker.check(f"{self.BASE_PATH}/null_scrapper_uc.json")

        with self.assertRaises(NotAJsonListException):
            UCFChecker.check(f"{self.BASE_PATH}/invalid_scrapper.json")

    def test_no_ucs(self):
        with self.assertRaises(EmptyConfigFileException):
            UCFChecker.check(f"{self.BASE_PATH}/irrelevant.json")

    def test_wrong_waiting(self):
        with self.assertRaises(WaitingException):
            UCFChecker.check(f"{self.BASE_PATH}/waiting_misstyped.json")

        with self.assertRaises(WaitingException):
            UCFChecker.check(f"{self.BASE_PATH}/waiting_out_of_bounds.json")

    def test_invalid_str_fields(self):
        with self.assertRaises(ScrapperUCException):
            UCFChecker.check(f"{self.BASE_PATH}/invalid_scrapper_ucs.json")

        with self.assertRaises(SpecificStrFieldException):
            UCFChecker.check(f"{self.BASE_PATH}/invalid_specific_str_field.json")

        with self.assertRaises(CommonStrFieldException):
            UCFChecker.check(f"{self.BASE_PATH}/invalid_common_str_field.json")

    def test_invalid_date_structure(self):

        with self.assertRaises(NotAJsonListException):
            UCFChecker.check(f"{self.BASE_PATH}/date_not_list.json")

        with self.assertRaises(NoSuchDateFieldException):
            UCFChecker.check(f"{self.BASE_PATH}/missing_months.json")

        with self.assertRaises(NoSuchDateFieldException):
            UCFChecker.check(f"{self.BASE_PATH}/missing_years.json")

        with self.assertRaises(DateFieldException):
            UCFChecker.check(f"{self.BASE_PATH}/date_null.json")

        with self.assertRaises(DateFieldException):
            UCFChecker.check(f"{self.BASE_PATH}/date_size_out_of_bounds.json")

    def test_invalid_date_values(self):

        with self.assertRaises(UnavailableScrapperException):
            UCFChecker.check(f"{self.BASE_PATH}/unavailable_scrapper.json")

        with self.assertRaises(DateFieldException):
            UCFChecker.check(f"{self.BASE_PATH}/date_not_int.json")

        with self.assertRaises(DateFieldException):
            UCFChecker.check(f"{self.BASE_PATH}/date_unordered.json")

        with self.assertRaises(YearsDateException):
            UCFChecker.check(f"{self.BASE_PATH}/years_out_of_bounds.json")

        with self.assertRaises(MonthsDateException):
            UCFChecker.check(f"{self.BASE_PATH}/months_out_of_bounds.json")

        with self.assertRaises(DaysDateException):
            UCFChecker.check(f"{self.BASE_PATH}/days_out_of_bounds.json")
