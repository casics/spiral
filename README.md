CASICS Spiral
==============

<img width="100px" align="right" src=".graphics/casics-logo-small.svg">

This module provides several different functions for splitting identifiers found in source code files.  The name _spiral_ is a loose acronym based on "_SPlitters for IdentifieRs: A Library_".

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/casics/spiral](https://github.com/casics/spiral)<br>
*License*:      Unless otherwise noted, this content is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.

☀ Introduction
-----------------------------

Natural language processing (NLP) methods are increasingly being applied to source code analysis for various purposes.  The methods rely on terms (identifiers and other textual strings) extracted from program source code and comments.  The methods often work better if, instead of raw identifiers, real words are used as features; that is, `read`, `From` and `File` are often better features for NLP tools than an identifier `readFromFile`.  This leads to the need for automated methods for splitting identifiers of classes, functions, variables, and other entities into word-like constituents.

Sometimes identifiers can be cryptic but meaningful to experienced human readers, but software lacks the intuition needed to make sense of them.  For example, human readers will naturally tend to interpret something like `getInt` this as meaning "get an integer", but software lacks human intuition and needs more help to glean meaning from `get` and `Int`.  One of the hypotheses underlying the approach being taken in CASICS is that machine learning algorithms may perform better if identifiers are not only split, but also expanded.  For this reason, we needed to implement advanced identifier splitting and elaboration algorithms.

_Spiral_ is a Python 3 package that implements numerous identifier splitting algorithms, as well as several identifier expansion algorithms.  It provides some basic naive splitting algorithms, such as straightforward camel-case splitter, as well as more elaborate heuristic splitters, such as an algorithm we call _ronin_ based on the Samurai algorithm by [Enslen, Hill, Pollock and Vija-Shanker, 2009](https://dl.acm.org/citation.cfm?id=1591139)).

⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/casics/spiral/issues) for this repository.

♬ Contributing &mdash; info for developers
------------------------------------------

A lot remains to be done on CASICS in many areas.  We would be happy to receive your help and participation if you are interested.  Please feel free to contact the developers either via GitHub or the mailing list [casics-team@googlegroups.com](casics-team@googlegroups.com).

Everyone is asked to read and respect the [code of conduct](CONDUCT.md) when participating in this project.

❤️ Acknowledgments
------------------

Funding for this and other CASICS work has come from the [National Science Foundation](https://nsf.gov) via grant NSF EAGER #1533792 (Principal Investigator: Michael Hucka).
