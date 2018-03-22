Tests
=====

`compare`
---------

The small program named `compare` in this directory is a utility I used during testing and development.  It which takes an oracle file as input, compares the splits produced by Ronin, and outputs the results.  Example of use:

```csh
./compare data/ludiso.tsv
./compare -l data/intt.tsv
```

The `-l` option is needed with the INTT data set because in that set, all the identifiers have been lower-cased in the expected results list.  The `-l` option makes `compare` lower-case the Ronin results before comparing them to the expected results.

Use the `-h` help option on `compare` to find out more about the command-line options it understands.

Tests for `py.test`
-------------------

The files whose names begin with `test_` are intended for use with the [py.test](https://pytest.org) testing framework.  You can run them by executing the following command in a terminal shell in this directory:

```csh
python3 -m py.test
```
