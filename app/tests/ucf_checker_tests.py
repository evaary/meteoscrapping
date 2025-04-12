from unittest import TestCase

from app.UCFChecker import UCFChecker
from app.boite_a_bonheur.UCFParameterEnum import UCFParameter
from app.exceptions.ucf_checker_exceptions import (DateFieldException,
                                                   DaysDateException,
                                                   MonthsDateException,
                                                   RequiredFieldException,
                                                   UnavailableScrapperException,
                                                   NoConfigFoundException,
                                                   NotAJsonFileException,
                                                   NotAJsonObjectException,
                                                   NotAJsonListException,
                                                   EmptyConfigFileException,
                                                   ScrapperUCException,
                                                   InvalidStrFieldException,
                                                   YearsDateException,
                                                   GeneralParametersFieldException)
from app.ucs_module import GeneralParametersUC


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
        "days_oob"            : f"{BASE_PATH}/days_out_of_bounds.json",
        "invalid_genparams"   : f"{BASE_PATH}/invalid_general_params.json",
        "max_cpus_oob"        : f"{BASE_PATH}/max_cpus_oob.json",
        "max_cpus_oob_2"      : f"{BASE_PATH}/max_cpus_oob_2.json",
        "invalid_parallelism" : f"{BASE_PATH}/invalid_parallelism.json",
        "fake_parallelism"    : f"{BASE_PATH}/fake_parallelism.json",
        "missing_field_genprm": f"{BASE_PATH}/missing_field_genparams.json",
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

        with self.assertRaises(RequiredFieldException):
            UCFChecker.check(self.CONFIG_FILES["invalid_specstr"])

        with self.assertRaises(InvalidStrFieldException):
            UCFChecker.check(self.CONFIG_FILES["invalid_comstr"])

    def test_invalid_date_structure(self):

        with self.assertRaises(NotAJsonListException):
            UCFChecker.check(self.CONFIG_FILES["date_not_list"])

        with self.assertRaises(DateFieldException):
            UCFChecker.check(self.CONFIG_FILES["missing_months"])

        with self.assertRaises(DateFieldException):
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

    def test_general_parameters(self):

        with self.assertRaises(NotAJsonObjectException):
            UCFChecker.check(self.CONFIG_FILES["invalid_genparams"])

        with self.assertRaises(GeneralParametersFieldException):
            UCFChecker.check(self.CONFIG_FILES["max_cpus_oob"])

        with self.assertRaises(GeneralParametersFieldException):
            UCFChecker.check(self.CONFIG_FILES["invalid_parallelism"])

        with self.assertRaises(RequiredFieldException):
            UCFChecker.check(self.CONFIG_FILES["missing_field_genprm"])

        config_file = UCFChecker.check(self.CONFIG_FILES["max_cpus_oob_2"])
        gpuc = GeneralParametersUC.from_json_object(config_file[UCFParameter.GENERAL_PARAMETERS.json_name])
        self.assertEqual(gpuc.cpus, UCFParameter.MAX_CPUS)

        config_file = UCFChecker.check(self.CONFIG_FILES["fake_parallelism"])
        gpuc = GeneralParametersUC.from_json_object(config_file[UCFParameter.GENERAL_PARAMETERS.json_name])
        self.assertFalse(gpuc._should_download_in_parallel)
