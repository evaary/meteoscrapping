from app.data_managers import from_json, to_csv, to_json
from app.scrappers import WundergroundScrapper, OgimetScrapper
from app.config_checker import ConfigFilesChecker
import os

def run():
    '''
    (1) définitions des chemins vers les répertoires utiles et des scrappers
    (2) listes des fichiers config contenus dans le répertoire et exclusion des éventuels
    fichiers qui n'en sont pas. Si aucun n'est trouvé, on quitte.
    (3) contrôle de la structure du fichier de configuration. Si le fichier n'est pas
    bon, on passe au fichier suivant.
    (4) récupération des données
    (5) enregistrement des données et des erreurs trouvées
    '''
    # (1)
    workdir = os.getcwd()
    paths = {
        "config": os.path.join(workdir, "config"),
        "results": os.path.join(workdir, "results"),
        "errors": os.path.join(workdir, "errors")
    }

    scrappers = {
        "ogimet": OgimetScrapper,
        "wunderground": WundergroundScrapper
    }

    '''identifiant pour nommer le fichier résultant d'un job'''
    job_id = 0

    # (2)
    try:
        config_files = [
            os.path.join(paths["config"], filename)
            for filename in os.listdir(paths["config"])
            if filename.startswith("config") and filename.endswith(".json")
        ]
    except:
        print(f"\n no config directory found in {workdir} \n")
        return

    if len(config_files) == 0:
        print(f"\n no config files in {paths['config']} \n")
        return

    for filename in config_files:

        print(filename)
        job_id += 1
        config = from_json(filename)
        # (3)
        checker = ConfigFilesChecker(config)
        if not checker.check():
            continue
        # (4)
        scrapper = scrappers[config["scrapper"]](config)
        data = scrapper.get_data()
        # (5)
        if len(data) != 0:
            path_res = os.path.join(paths["results"], f"{config['city']}_{config['scrapper']}_{job_id}.csv")
            to_csv(data, path_res)

        if len(scrapper.errors) != 0:
            path_err = os.path.join(paths["errors"], f"{config['city']}_{config['scrapper']}_{job_id}_errors.json")
            to_json(scrapper.errors, path_err)

        print("\n")


if __name__ == "__main__":
    run()