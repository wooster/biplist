2016-01-11 wooster v1.0.1
-------------------------

Adding back in Python 2.6 support. This will be removed again in a future version.

2016-01-09 wooster v1.0.0
-------------------------

This release changes the type of `Uid` from a subclass of `int` to a subclass of `object`.

This change was made to address GitHub issue [\#9 Ints are being turned into Uids and vice versa when both are present in a plist.](https://github.com/wooster/biplist/issues/9)

This release also bumps the minimum supported Python versions to 2.7 and 3.4.

2016-01-09 wooster v0.9.1
-------------------------

Fixes GitHub issue [\#8 ERROR: testLargeDates (test_valid.TestValidPlistFile)](https://github.com/wooster/biplist/issues/8)

Fixes [\#6 Empty Data object converted as empty string](https://bitbucket.org/wooster/biplist/issues/6/empty-data-object-converted-as-empty)

Creates 1-byte strings when possible, per [PR \#4](https://bitbucket.org/wooster/biplist/pull-requests/4/create-1-byte-strings-when-possible-and/diff)

2014-10-26 wooster v0.9
-----------------------

Fixes [\#5 ValueError: timestamp out of range for platform time_t](https://bitbucket.org/wooster/biplist/issue/5/valueerror-timestamp-out-of-range-for)

Merged pull request [\#3 removing the `six` module while keeping Python3 compatibility](https://bitbucket.org/wooster/biplist/pull-request/3)

2014-08-17 wooster v0.8 
-----------------------

Fixes [\#3 testFileRead fails using python 3.x](https://bitbucket.org/wooster/biplist/issue/3/testfileread-fails-using-python-3x) 
along with several other Python 3 compatibility issues.
