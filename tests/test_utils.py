import os

def data_path(path):
    return os.path.join(os.path.dirname(globals()["__file__"]), 'data', path)
