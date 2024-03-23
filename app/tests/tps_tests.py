from unittest import TestCase

from app.ucs.UserConfigFile import UserConfigFile


class TPsTester(TestCase):

    BASE_PATH = "./app/tests/ucfs"

    def test_nominal_case(self):
        ucf = UserConfigFile.from_json(f"{self.BASE_PATH}/correct.json")

        otps = [ouc for ouc in ucf.get_ogimet_ucs() if ouc.city == "Ferrara"][0].to_tps()
        wtps = ucf.get_wunderground_ucs()[0].to_tps()
        mdtps = [muc for muc in ucf.get_meteociel_ucs() if len(muc.days) == 0][0].to_tps()
        mhtps = [muc for muc in ucf.get_meteociel_ucs() if len(muc.days) != 0][0].to_tps()

        self.assertEqual(len(wtps), 6)
        self.assertEqual(len(otps), 1)
        self.assertEqual(len(mdtps), 2)
        self.assertEqual(len(mhtps), 2)
