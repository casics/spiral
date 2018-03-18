Data files for testing Spiral
=============================

This directory contains data used for testing Spiral's ability to split identifiers.  It currently consists of two "oracle" files (i.e., sets of identifiers together with their splits, based on human or other validation):

1. The _Loyola University of Delaware Identifier Splitting Oracle_ (Ludiso).  The files came from this website as it existed on 2017-02-18: [http://www.cs.loyola.edu/~binkley/ludiso/](http://www.cs.loyola.edu/~binkley/ludiso/)
2. The INTT data set, extracted from the zip archive of INTT put online in 2011 at the following website: [http://oro.open.ac.uk/28352/](http://oro.open.ac.uk/28352/)

The files in this directory are in tab-separated (TSV) form.  Each row has two columns:

    identifer	each,token,split,separated,by,commas

The second column shows the split version of the identifier with each token separated by commas.  Here is an example:

    windowspan	window,span

The [archived](archived) subdirectory contains archived versions of the original materials from which the `.tsv` files in this directory were created.
