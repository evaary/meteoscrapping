from unittest import TestCase

from app.Runner import Runner


class RunnerTester(TestCase):

    CONFIG = {  "waiting": 3,

                "ogimet":[ {"ind"   : "16138",
                            "__city"  : "Ferrara",
                            "year"  : [2021],
                            "month" : [2] } ],

                "wunderground":[ {  "country_code"  : "it",
                                    "region"        : "LIBD",
                                    "__city"          : "matera",
                                    "year"          : [2021],
                                    "month"         : [1] } ],

                "meteociel":[ { "code_num"  : "2",
                                "code"      : "7249",
                                "__city"      : "orleans",
                                "year"      : [2020],
                                "month"     : [2] } ],

                "meteociel_daily":[ {   "code_num"  : "2",
                                        "code"      : "7249",
                                        "__city"      : "orleans",
                                        "year"      : [2020],
                                        "month"     : [2],
                                        "day"       : [27,31] } ] }

    def test_all_configs(self):

        all_configs = Runner._get_all_configs(self.CONFIG)
        self.assertEqual(len(all_configs), 4)
        self.assertTrue( all( [ "waiting" in config.keys() for config in all_configs ] ) )
        self.assertTrue( all( [ any( [ config["scrapper"] == scrapper
                                       for config in all_configs ] )

                                for scrapper in self.CONFIG.keys() if scrapper != "waiting"] ) )

    def test_filenames(self):

        all_configs = Runner._get_all_configs(self.CONFIG)
        ogimet_config = list( filter( lambda config: config["scrapper"] == "ogimet" ,  all_configs) )[0]

        data, errors = Runner._create_data_and_errors_filenames(ogimet_config)
        ref_data = f"{ogimet_config['__city']}_ogimet.csv".lower()
        ref_errors = f"{ogimet_config['__city']}_ogimet_errors.json".lower()

        data: str
        errors: str

        self.assertTrue( data.endswith(ref_data) )
        self.assertTrue( errors.endswith(ref_errors) )
