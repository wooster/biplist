# Testing Information


## Running Tests with Tox

Tests can be run across several Python versions using tox.

The `tox.ini` file specifies the environments the tests are to be run against. When tox is installed, you can run `tox` from the top level directory to run the tests in each environemnt. More info is available at the [`tox` page](https://tox.readthedocs.io/en/latest/).

## Fuzzing with afl

Fuzzing with afl is a useful way to find interesting bugs. To start, install `afl-fuzz` and `python-afl`. Then, create a simple test driver in the top level dir like:

```
import sys

import afl

from biplist import *

afl.init()

try:
    s = sys.stdin.read()
    readPlistFromString(s)
except InvalidPlistException:
    pass
except UnicodeDecodeError:
    pass
```

Create a directory full of example plists for `afl` to fuzz `biplist` against. For this, I've used a collection of valid plists and placed them in a directory called `fuzz_examples`. Then, run `py-afl-fuzz`:

`py-afl-fuzz -o results/ -i fuzz_examples/ -- /usr/local/bin/python fuzz.py`

Plists which crash biplist and are found via fuzzing should go in the `fuzz_data` directory, and tests against those plists should go in the `test_fuzz_results.py` file.

## Resources

* [american fuzzy lop](http://lcamtuf.coredump.cx/afl/)
* [Introduction to Fuzzing in Python with AFL](https://alexgaynor.net/2015/apr/13/introduction-to-fuzzing-in-python-with-afl/)
