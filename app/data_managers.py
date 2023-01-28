import json
import os

# version 27/01/2022

def create_dirs(data_saver):
    """Functions to automatically create dirs, if needed, before saving files in."""
    def wrapper_function(*args, **kwargs):

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


"""data is a dict or a list"""
@create_dirs
def to_json(data, path):
    with open(path, encoding="utf-8", mode="w") as jsonfile:
        json.dump(data, jsonfile, indent=4)

""" figure is a matplotlib Figure object"""
@create_dirs
def to_png(figure, path):
    figure.savefig(path)

"""data is a pandas DataFrame object"""
@create_dirs
def to_csv(data, path, index=False):
    data.to_csv(path, index=index)

"""data is a str"""
@create_dirs
def to_txt(data, path):
    with open(path, mode="w", encoding="utf-8") as f:
        f.write(f"{data}")

def from_json(path):
    with open(path, mode="r", encoding="utf-8") as jsonfile:
        return json.load(jsonfile)

def from_txt(path, _next=None):
    with open(path, mode="r", encoding="utf-8") as txtfile:
        try:
            for _ in range(_next):
                next(txtfile)
        except:
            pass

        return txtfile.read()
