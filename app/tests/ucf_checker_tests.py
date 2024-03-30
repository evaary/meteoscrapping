from unittest import TestCase

from app.ucs.UCFChecker import UCFChecker
from app.ucs.ucf_checker_exceptions import (DateFieldException,
                                            DaysDateException,
                                            MonthsDateException,
                                            NoSuchDateFieldException,
                                            UnavailableScrapperException,
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

    CONFIG_FILES = {
        "correct"             : f"{BASE_PATH}/correct.json",
        "empty"               : f"{BASE_PATH}/empty.json",
        "malformed"           : f"{BASE_PATH}/malformed.json",
        "wrong_config"        : f"{BASE_PATH}/wrong_config.json",
        "null_scrapper_uc"    : f"{BASE_PATH}/null_scrapper_uc.json",
        "invalid_scrapper"    : f"{BASE_PATH}/invalid_scrapper.json",
        "irrelevant"          : f"{BASE_PATH}/irrelevant.json",
        "invalid_scrapper_ucs": f"{BASE_PATH}/invalid_scrapper_ucs.json",
        "invalid_specstr"     : f"{BASE_PATH}/invalid_specific_str_field.json",
        "invalid_comstr"      : f"{BASE_PATH}/invalid_common_str_field.json",
        "date_not_list"       : f"{BASE_PATH}/date_not_list.json",
        "missing_months"      : f"{BASE_PATH}/missing_months.json",
        "missing_years"       : f"{BASE_PATH}/missing_years.json",
        "date_null"           : f"{BASE_PATH}/date_null.json",
        "date_size_oob"       : f"{BASE_PATH}/date_size_out_of_bounds.json",
        "unavailable_scrapper": f"{BASE_PATH}/unavailable_scrapper.json",
        "date_not_int"        : f"{BASE_PATH}/date_not_int.json",
        "date_unordered"      : f"{BASE_PATH}/date_unordered.json",
        "years_oob"           : f"{BASE_PATH}/years_out_of_bounds.json",
        "months_oob"          : f"{BASE_PATH}/months_out_of_bounds.json",
        "days_oob"            : f"{BASE_PATH}/days_out_of_bounds.json"
    }

    def test_nominal_case(self):
        try:
            UCFChecker.check(self.CONFIG_FILES["correct"])
        except Exception:
            self.fail("UCFCheckerTester : le cas nominal ne fonctionne pas")

    def test_broken_configs(self):
        with self.assertRaises(NoConfigFoundException):
            UCFChecker.check(f"bouh")

        with self.assertRaises(NotAJsonFileException):
            UCFChecker.check(self.CONFIG_FILES["empty"])

        with self.assertRaises(NotAJsonFileException):
            UCFChecker.check(self.CONFIG_FILES["malformed"])

    def test_structure_errors_configs(self):
        with self.assertRaises(NotAJsonObjectException):
            UCFChecker.check(self.CONFIG_FILES["wrong_config"])

        with self.assertRaises(ScrapperUCException):
            UCFChecker.check(self.CONFIG_FILES["null_scrapper_uc"])

        with self.assertRaises(NotAJsonListException):
            UCFChecker.check(self.CONFIG_FILES["invalid_scrapper"])

    def test_no_ucs(self):
        with self.assertRaises(EmptyConfigFileException):
            UCFChecker.check(self.CONFIG_FILES["irrelevant"])

    def test_invalid_str_fields(self):
        with self.assertRaises(ScrapperUCException):
            UCFChecker.check(self.CONFIG_FILES["invalid_scrapper_ucs"])

        with self.assertRaises(SpecificStrFieldException):
            UCFChecker.check(self.CONFIG_FILES["invalid_specstr"])

        with self.assertRaises(CommonStrFieldException):
            UCFChecker.check(self.CONFIG_FILES["invalid_comstr"])

    def test_invalid_date_structure(self):

        with self.assertRaises(NotAJsonListException):
            UCFChecker.check(self.CONFIG_FILES["date_not_list"])

        with self.assertRaises(NoSuchDateFieldException):
            UCFChecker.check(self.CONFIG_FILES["missing_months"])

        with self.assertRaises(NoSuchDateFieldException):
            UCFChecker.check(self.CONFIG_FILES["missing_years"])

        with self.assertRaises(DateFieldException):
            UCFChecker.check(self.CONFIG_FILES["date_null"])

        with self.assertRaises(DateFieldException):
            UCFChecker.check(self.CONFIG_FILES["date_size_oob"])

    def test_invalid_date_values(self):

        with self.assertRaises(UnavailableScrapperException):
            UCFChecker.check(self.CONFIG_FILES["unavailable_scrapper"])

        with self.assertRaises(DateFieldException):
            UCFChecker.check(self.CONFIG_FILES["date_not_int"])

        with self.assertRaises(DateFieldException):
            UCFChecker.check(self.CONFIG_FILES["date_unordered"])

        with self.assertRaises(YearsDateException):
            UCFChecker.check(self.CONFIG_FILES["years_oob"])

        with self.assertRaises(MonthsDateException):
            UCFChecker.check(self.CONFIG_FILES["months_oob"])

        with self.assertRaises(DaysDateException):
            UCFChecker.check(self.CONFIG_FILES["days_oob"])
