CASICS Spiral
==============

<img width="100px" align="right" src=".graphics/casics-logo-small.svg">

This module provides several different functions for splitting identifiers found in source code files.  The name _spiral_ is a loose acronym based on "_SPlitters for IdentifieRs: A Library_".

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/casics/spiral](https://github.com/casics/spiral)<br>
*License*:      Unless otherwise noted, this content is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.

☀ Introduction
-----------------------------

When analyzing source code, and especially when attempting to train machine learning algorithms to recognize features in source code, a useful operation is to split program identifiers.  For example, a function name such as `getInt` could be split into `get` and `Int`, and the result could be treated as a short phrase.  Human readers will naturally tend to interpret this as meaning "get integer", but software lacks human intuition and needs more help to glean meaning from `get` and `Int`.  In CASICS, we have the hypothesis that machine learning algorithms may perform better if identifiers are not only split, but also elaborated: `get` and `Int` could perhaps be turned into the sequence `['get', 'Integer']` if we applied some heuristics about commonly-used abbreviations.

_Spiral_ is a library of functions for splitting and elaborating identifier strings found in source code.  It provides some basic naive algorithms, such as straightforward camel-case splitter, as well as more elaborate heuristic splitters, such as the Samurai algorithm ([Enslen et al., "Mining source code to automatically split identifiers for software analysis", MSR'09.](https://dl.acm.org/citation.cfm?id=1591139)).


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
