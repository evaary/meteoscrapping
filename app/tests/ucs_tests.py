import copy
from unittest import TestCase

from app.boite_a_bonheur.ScrapperTypeEnum import ScrapperTypes
from app.UserConfigFile import UserConfigFile


class UCsTester(TestCase):

    BASE_PATH = "./app/tests/ucfs"

    CONFIG_FILES = {"correct"      : f"{BASE_PATH}/correct.json",
                    "duplicate_suc": f"{BASE_PATH}/duplicate_scrapper_uc.json"}

    def test_nominal_case(self):
        try:
            ucf = UserConfigFile.from_json(self.CONFIG_FILES["correct"])
        except Exception:
            self.fail("ScrapperUCsTests : le cas nominal ne fonctionne pas")

        self.assertEqual(len(ucf.ogimet_ucs), 8)
        self.assertEqual(len(ucf.meteociel_ucs), 8)
        self.assertEqual(len(ucf.wunderground_ucs), 2)

    def test_duplicated_uc(self):
        ucf = UserConfigFile.from_json(self.CONFIG_FILES["duplicate_suc"])
        self.assertEqual(len(ucf.wunderground_ucs), 1)

    def test_dates(self):
        ucf = UserConfigFile.from_json(self.CONFIG_FILES["correct"])
        m_with_0 = [uc
                    for uc in ucf.meteociel_ucs
                    if uc.city == "m_with_0"][0]

        d_with_0 = [uc
                    for uc in ucf.meteociel_ucs
                    if uc.city == "d_with_0"][0]

        self.assertEqual(m_with_0.dates[0], "2/2021")
        self.assertEqual(d_with_0.dates[0], "1/2/2021")

    def test_equals(self):

        ucf = UserConfigFile.from_json(self.CONFIG_FILES["correct"])

        muc_1 = ucf.meteociel_ucs[0]
        muc_2 = ucf.meteociel_ucs[1]
        muc_1_clone = copy.deepcopy(muc_1)

        self.assertEqual(muc_1, muc_1)
        self.assertEqual(muc_1, muc_1_clone)
        self.assertEqual(muc_1_clone, muc_1)
        self.assertNotEqual(muc_1, muc_2)
        self.assertNotEqual(muc_1, None)
        self.assertNotEqual(muc_1, dict({"bouh": 3}))

        muc_1_clone._scrapper_type = ScrapperTypes.WUNDERGROUND_DAILY
        self.assertNotEqual(muc_1, muc_1_clone)

    def test_hashcode(self):

        ucf = UserConfigFile.from_json(self.CONFIG_FILES["correct"])

        muc_1 = ucf.meteociel_ucs[0]
        muc_2 = ucf.meteociel_ucs[1]
        muc_1_clone = copy.deepcopy(muc_1)

        self.assertEqual(hash(muc_1), hash(muc_1))
        self.assertEqual(hash(muc_1), hash(muc_1_clone))
        self.assertNotEqual(hash(muc_1), hash(muc_2))
