Spiral data files
=================

The following are the data files located in this subdirectory.


`frequencies.pklz` and `frequencies.csv`
----------------------------------------

A compressed Python pickle file containing a Python `dict` object.  It constitutes a table of token frequencies that was created from an analysis of over 46,000 randomly selected software projects in GitHub that contained at least one Python source code file.  This file contains only those entries that had frequencies of at least 10; the full (and much larger) table is in `frequencies-full.csv`.  The `frequencies.csv` file is a CSV version of the data in the Python dictionary contained in `frequencies.pklz`.


`frequencies-full.pklz` and `frequencies-full.csv`
--------------------------------------------------

A compressed Python pickle file containing a Python `dict` object.  It constitutes a table of token frequencies that was created from an analysis of over 46,000 randomly selected software projects in GitHub that contained at least one Python source code file.  The tokens were extracted using software from Spiral's parent project, [CASICS](https://github.com/casics) (specifically, the [extractor](https://github.com/casics/extractor) package), and the frequency table constructed using a procedure encoded in the small program `create_frequency_file` [included with Spiral](../../utils/create_frequency_file).


`dictionary.pklz`
-----------------

The Python `set` contained in this compressed Python pickle was created in part using the `word` and `wordnet` datasets from [NTLK](https://github.com/nltk).  The `word` dictionary is public domain, but the `wordnet` dictionary is copyright 2006 by Princeton University and made available under [license terms](https://wordnet.princeton.edu/license-and-commercial-use) that permit free redistribution.  The following is full statement for WordNet:

<blockquote>
WordNet 3.0 license: (Download)

WordNet Release 3.0 This software and database is being provided to you, the LICENSEE, by Princeton University under the following license. By obtaining, using and/or copying this software and database, you agree that you have read, understood, and will comply with these terms and conditions.: Permission to use, copy, modify and distribute this software and database and its documentation for any purpose and without fee or royalty is hereby granted, provided that you agree to comply with the following copyright notice and statements, including the disclaimer, and that the same appear on ALL copies of the software, database and documentation, including modifications that you make for internal use or for distribution. WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved. THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES OF MERCHANT- ABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS. The name of Princeton University or Princeton may not be used in advertising or publicity pertaining to distribution of the software and/or database. Title to copyright in this software, database and any associated documentation shall at all times remain with Princeton University and LICENSEE agrees to preserve same.
</blockquote>
