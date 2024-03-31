from unittest import TestCase

from app.ucs.UserConfigFile import UserConfigFile


class TPsTester(TestCase):

    BASE_PATH = "./app/tests/ucfs"

    CONFIG_FILES = {
        "correct": f"{BASE_PATH}/correct.json"
    }

    def test_nominal_case(self):
        ucf = UserConfigFile.from_json(self.CONFIG_FILES["correct"])

        otps = [ouc for ouc in ucf.ogimet_ucs if ouc.city == "Ferrara"][0].to_tps()
        wtps = ucf.wunderground_ucs[0].to_tps()
        mdtps = [muc for muc in ucf.meteociel_ucs if len(muc.days) == 0][0].to_tps()
        mhtps = [muc for muc in ucf.meteociel_ucs if len(muc.days) != 0][0].to_tps()

        self.assertEqual(sum([1 for _ in wtps]), 6)
        self.assertEqual(sum([1 for _ in otps]), 1)
        self.assertEqual(sum([1 for _ in mdtps]), 2)
        self.assertEqual(sum([1 for _ in mhtps]), 2)
