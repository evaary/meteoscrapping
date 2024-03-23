import json
import os

import pandas as pd


def create_dirs(data_saver):

    def wrapper_function(*args, **kwargs):
        # création du répertoire de sauvegarde s'il n'existe pas
        try:
            dirs, _ = os.path.split(kwargs["path"])
        except KeyError:
            dirs, _ = os.path.split(args[1])

        try:
            os.makedirs(dirs)
        except (FileExistsError, FileNotFoundError):
            pass

        return data_saver(*args, **kwargs)

    return wrapper_function


@create_dirs
def to_json(data, path):
    with open(path, encoding="utf-8", mode="w") as jsonfile:
        json.dump(data, jsonfile, indent=4)


@create_dirs
def to_csv(data: pd.DataFrame, path, index=False):
    data.to_csv(path, index=index)


def from_json(path):
    with open(path, mode="r", encoding="utf-8") as jsonfile:
        return json.load(jsonfile)
