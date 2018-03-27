---
title: 'Spiral: splitters for identifiers in source code files'
tags:
- source code mining
- text processing
- machine learning
authors:
- name: Michael Hucka
  orcid: 0000-0001-9105-5960
  affiliation: 1
affiliations:
- name: Department of Computing and Mathematical Sciences, California Institute of Technology, Pasadena, CA 91125, USA
  index: 1
date: 28 March 2018
bibliography: paper.bib
---

# Summary

_Spiral_ is a Python 3 package that implements numerous identifier splitting algorithms.  _Identifier splitting_ (also known as _identifier name tokenization_) is the task of breaking apart program identifier strings such as `getInt` or `readUTF8stream` into component tokens: [`get`, `int`] and [`read`, `UTF8`, `stream`].  The need for splitting identifiers arises in a variety of contexts, including natural language processing (NLP) methods applied to source code analysis and program comprehension.

Spiral is easy to use.  Here are some examples of calling the Ronin splitter algorithm on inputs that would challenge simpler splitters.  The following Python code,

```python
  from spiral import ronin
  for s in [ 'mStartCData', 'nonnegativedecimaltype', 'getUtf8Octets',
             'savefileas', 'nbrOfbugs']:
      print(ronin.split(s))
```

produces the following output:

```python
  ['m', 'Start', 'C', 'Data']
  ['nonnegative', 'decimal', 'type']
  ['get', 'Utf8', 'Octets']
  ['save', 'file', 'as']
  ['nbr', 'Of', 'bugs']
  ```

Spiral also includes a command-line program named `spiral`; it will split strings provided on the command line or in a file, and is useful for experimenting with Spiral.


# The need for sophisticated splitting algorithms

Splitting identifiers is deceptively difficult and remains a research problem for which no perfect solution exists today.  Even in cases where the input consists of identifiers that strictly follow conventions such as camel case, ambiguities can arise.  For example, to split `J2SEProjectTypeProfiler` into [`J2SE`, `Project`, `Type`, `Profiler`] requires the reader to recognize `J2SE` as a unit.  The task of splitting identifiers is made more difficult when there are no case transitions or other obvious boundaries in an identifier.

Spiral provides some several basic naive splitting algorithms, such as a straightforward camel-case splitter, as well as more elaborate heuristic splitters, including a novel algorithm we call _Ronin_.  Ronin uses a variety of heuristic rules, English dictionaries, and tables of token frequencies obtained from mining source code repositories.  It includes a default table of term frequencies derived from an analysis of over 46,000 randomly selected software projects in GitHub that contained at least one Python source code file.


# Splitters available in Spiral

The following table lists the splitters implemented in Spiral at this time:

| Splitter name | Operation |
|----------------|---------------------------------------|
| `delimiter_split` | split only at characters `$` `~` `_` `.` `:` `/` `@` |
| `digit_split` | split only at digits |
| `pure_camelcase_split` | split at forward camel case transitions (lower to upper case) |
| `safe_simple_split` | split at hard delimiter characters and forward camel case only; won't split strings that don't follow strict camel case |
| `simple_split` | split at hard delimiter characters and forward camel case, even if a string doesn't follow strict camel case conventions |
| `elementary_split` | split by hard delimiters, forward camel case, and digits |
| `heuristic_split` | split by hard delimiters, forward camel case, and digits, but recognize special cases such as `utf8`, `sha256`, etc. |
| _Samurai_ | frequency-based approach published in the literature |
| _Ronin_ | frequency-based approach originally based on Samurai |

The name "Ronin" is a play on the use of the name "Samurai" [@Enslen2009-gk] for their identifier splitting algorithm.  The core loop of Ronin is based on Samurai, but substantially modified and extended.  A goal for Ronin was to produce a splitter that had good performance using only a global table of token frequencies, without the need for an additional table of frequencies mined from the source code currently being analyzed.  This makes Ronin usable even without preprocessing a code base to extract token frequencies.

The name _Spiral_ is a loose acronym based on "_SPlitters for IdentifieRs: A Library_".


# Acknowledgments

This material is based upon work supported by the [National Science Foundation](https://nsf.gov) under Grant Number 1533792.  Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.


# References
