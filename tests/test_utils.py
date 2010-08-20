import os

def fixture_path(path):
    return os.path.join(os.path.dirname(globals()["__file__"]), 'fixtures', path)
