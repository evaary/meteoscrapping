import copy
from unittest import TestCase

from app.ucs.UserConfigFile import UserConfigFile


class UCsTester(TestCase):

    BASE_PATH = "./app/tests/ucfs"

    CONFIG_FILES = {
        "correct"      : f"{BASE_PATH}/correct.json",
        "duplicate_suc": f"{BASE_PATH}/duplicate_scrapper_uc.json",
    }

    def test_nominal_case(self):
        try:
            ucf = UserConfigFile.from_json(self.CONFIG_FILES["correct"])
        except Exception:
            self.fail("ScrapperUCsTests : le cas nominal ne fonctionne pas")

        self.assertEqual(len(ucf.get_ogimet_ucs()), 2)
        self.assertEqual(len(ucf.get_meteociel_ucs()), 2)
        self.assertEqual(len(ucf.get_wunderground_ucs()), 1)

    def test_duplicated_uc(self):
        ucf = UserConfigFile.from_json(self.CONFIG_FILES["duplicate_suc"])
        self.assertEqual(len(ucf.get_wunderground_ucs()), 1)

    def test_equals(self):

        ucf = UserConfigFile.from_json(self.CONFIG_FILES["correct"])

        muc_1 = ucf.get_meteociel_ucs()[0]
        muc_2 = ucf.get_meteociel_ucs()[1]
        muc_1_clone = copy.deepcopy(muc_1)

        self.assertEqual(muc_1, muc_1)
        self.assertEqual(muc_1, muc_1_clone)
        self.assertEqual(muc_1_clone, muc_1)
        self.assertNotEqual(muc_1, muc_2)
        self.assertNotEqual(muc_1, None)
        self.assertNotEqual(muc_1, dict({"bouh": 3}))

        # TODO à fixer
        # muc_1_clone.__scrapper_type = ScrapperType.WUNDERGROUND_DAILY
        # self.assertNotEqual(muc_1, muc_1_clone)

    def test_hashcode(self):

        ucf = UserConfigFile.from_json(self.CONFIG_FILES["correct"])

        muc_1 = ucf.get_meteociel_ucs()[0]
        muc_2 = ucf.get_meteociel_ucs()[1]
        muc_1_clone = copy.deepcopy(muc_1)

        self.assertEqual(hash(muc_1), hash(muc_1))
        self.assertEqual(hash(muc_1), hash(muc_1_clone))
        self.assertNotEqual(hash(muc_1), hash(muc_2))
