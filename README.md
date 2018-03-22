Spiral<img width="130px" align="right" src=".graphics/spiral.svg">
=======

Spiral is a Python module that provides several different functions for splitting identifiers found in source code files.  The name _Spiral_ is a loose acronym based on "_SPlitters for IdentifieRs: A Library_".

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.4+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest version](https://img.shields.io/badge/Latest_version-1.0.0-green.svg?style=flat-square)](http://shields.io)

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/casics/spiral](https://github.com/casics/spiral)<br>
*License*:      Unless otherwise noted, this content is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.

Table of Contents
-----------------

* [Introduction](#-introduction)
* [Installation instructions](#-installation-instructions)
   * [Install dependencies](#-install-dependencies)
   * [Download and install Spiral](#-download-and-install-spiral)
* [Basic operation](#︎-basic-operation)
* [Performance of Ronin](#-performance-of-ronin)
* [Other splitters in Spiral](#%EF%B8%8F-other-splitters-in-spiral)
* [Limitations](#️-limitations)
* [More information](#-more-information)
* [Getting help and support](#-getting-help-and-support)
* [Contributing — info for developers](#-contributing--info-for-developers)
* [Acknowledgments](#️-acknowledgments)

☀ Introduction
-----------------------------

_Spiral_ is a Python 3 package that implements numerous identifier splitting algorithms.  _Identifier splitting_ (also known as _identifier name tokenization_) is the task of breaking apart program identifier strings such as `getInt` or `readUTF8stream` into component tokens: [`get`, `int`] and [`read`, `utf8`, `stream`].  The need for splitting identifiers arises in a variety of contexts, including natural language processing (NLP) methods applied to source code analysis and program comprehension.  Spiral provides some basic naive splitting algorithms, such as a straightforward camel-case splitter, as well as more elaborate heuristic splitters, such as an algorithm we call _Ronin_.

✺ Installation instructions
---------------------------

### ⓵&nbsp;&nbsp; _Check and install dependencies_

Spiral uses a number of Python modules that may or may not be installed in your Python environment.  Depending on the approach you use to install Spiral, you may or may not need to install them separately:

* [NLTK](https://www.nltk.org/install.html), particularly `nltk_words` and `ntlk_wordnet` from the `nltk.corpus` module and the `nltk.stem` module.
* [plac](https://pypi.python.org/pypi/plac), a command line arguments parser.
* [Platypus](http://platypus.readthedocs.io/en/latest/), a multiobject optimization library (but only if you want to optimize new parameter values)

### ⓶&nbsp;&nbsp; _Download and install Spiral_

The following is probably the simplest and most direct way to install Spiral on your computer:
```sh
sudo pip3 install git+https://github.com/casics/spiral.git
```

Alternatively, you can clone this repository and then run `setup.py`:
```sh
git clone https://github.com/casics/spiral.git
cd spiral
sudo python3 setup.py install
```

▶︎ Basic operation
------------------

Spiral is extremely easy to use.  To use a Spiral splitter in a Python program, simply import a splitter and then call it.

```python
from spiral.simple_splitters import pure_camelcase_split
print(pure_camelcase_split('TestString'))

```

Some splitters take optional parameters, and the more complex splitters have an `init()` function that you can optionally call to set additional parameters or load data.  Currently, only Ronin and Samurai have initialization functions, and calling `init()` is optional&mdash;if you do not call it, Ronin and Samurai will call their `init()` functions automatically.

Here are some examples of using the Ronin splitter algorithm.  The following input,

```python
from spiral import ronin
for s in [ 'mStartCData', 'nonnegativedecimaltype', 'getUtf8Octets', 'GPSmodule', 'savefileas', 'nbrOfbugs']:
    print(ronin.split(s))
```

produces the following output:

```python
['m', 'Start', 'C', 'Data']
['nonnegative', 'decimal', 'type']
['get', 'Utf8', 'Octets']
['GPS', 'module']
['save', 'file', 'as']
['nbr', 'Of', 'bugs']
```

Spiral also includes a command-line program named `spiral` in the [bin](bin) subdirectory; it will split strings provided on the command line or in a file, and is useful for experimenting with Spiral.  (_**Note**_: Ronin and Samurai first load internal data files, which causes a start-up delay.  In normal usage, called from an application, Spiral will only load the data once at first invocation and subsequent calls will be fast.  However, the command-line program can't save the data across invocations, so the startup cost occurs every time.  This is only a one-time startup delay and not typical for normal Spiral usage.)


🎯 Performance of Ronin
----------------------

Splitting identifiers is deceptively difficult.  It is a research-grade problem for which no perfect solution exists.  Even in cases where the input consists of identifiers that strictly follow conventions such as camel case, ambiguities can arise.  For example, correctly splitting `J2SEProjectTypeProfiler` into `J2SE`, `Project`, `Type`, `Profiler` requires the reader to recognize `J2SE` as a unit.  The task of splitting identifiers is made more difficult when there are no case transitions or other obvious boundaries in an identifier.  And then there is the small problem that humans are often simply inconsistent!

Ronin is an advanced splitter that uses a variety of heuristic rules, English dictionaries, and tables of token frequencies obtained from mining source code repositories.  Ronin includes a default table of term frequencies derived from an analysis of over 46,000 randomly selected software projects in GitHub that contained at least one Python source code file.  The tokens were extracted using software from Spiral's parent project, [CASICS](https://github.com/casics) (specifically, the [extractor](https://github.com/casics/extractor) package), and the frequency table constructed using a procedure encoded in the small program `create_frequency_file` [included with Spiral](utils/create_frequency_file).  Ronin also has a number of parameters that need to be tuned; this can be done using the optimization program `optimize-ronin` [in the dev/optimization subdirectory](dev/optimization/optimize-ronin).  The default parameter values were derived by optimizing performance against two data sets available from other research groups:

1. The [Loyola University of Delaware Identifier Splitting Oracle (Ludiso)](http://www.cs.loyola.edu/~binkley/ludiso/)
2. The INTT data set, extracted from the [zip archive of INTT](http://oro.open.ac.uk/28352/)

Spiral includes copies of these data sets in the [tests/data](tests/data) subdirectory.  The parameters derived primarily by running against the INTT database of 18,772 identifiers and their splits.  The following table summarizes the results:

| Data set                          | Number of splits matched by Ronin | Total in data set | Accuracy |
|-----------------------------------|------------------------:|---------------:|----------:|
| [INTT](tests/data/intt.tsv)       |                 17,287   | 18,772          | 92.09%   |
| [Ludiso](tests/data/ludiso.tsv)   |                 2,248    | 2,663           | 84.42%   |

Many of the "failures" against these sets of identifiers are actually not failures, but cases where Ronin gets a more correct answer or where there is a legitimate difference in interpretation.  Here are some examples:

| Identifier | Ludiso result | Ronin split |
|------------|---------------|-------------|
| `a.ecart`         | `a` `ecart` | `a` `e` `cart` |
| `ConvertToAUTF8String` | `Convert` `To` `AUTF` `8` `String` | `Convert` `To` `A` `UTF8` `String` |
| `MAPI_BCC`        | `MAPI` `BCC` | `M` `API` `BCC` |
| `GetWSIsEnabled`  | `Get` `WSIs` `Enabled` | `Get` `WS` `Is` `Enabled` |
| `fread`           | `fread` | `f` `read` |
| `FF_LOSS_COLORSPACE` |  `FF` `LOSS` `COLORSPACE` | `FF` `LOSS` `COLOR` `SPACE` |
| `m_bFilenameMode` | `m` `b` `File` `name` `Mode` | `m` `b` `Filename` `Mode` |

Names like `fread` could be considered appropriate to leave alone, but the `f` in `fread` actually stands for "file", and thus IMHO it makes sense to split it&mdash;splitting identifiers into meaningful tokens is the purpose of Ronin, after all.  Conversely, tokens such as `Utf8` should be left as units because they are meaningful.  Differences involving some other terms such as `color space` are due to Ronin splitting terms that are typically considered separate words but are treated as one word in Ludiso, or vice versa.  (The main entry in Wikipedia for "color space" is two words, while for "filename" it is one word.)  This sometimes also arises because Ronin recognizes prefixes and sometimes does not split words because they would not be in normal written English, such as `nonblocking` instead of `non` `blocking`.  Still other differences between Ronin's output and the expected splits given in Ludiso and INTT are due to inconsistencies in the Ludiso and INTT data sets.  For example, sometimes a token within a larger identifier is split in one case but not in another.  Finally, some other differences are cases where the Ludiso split seems to favor program-specific names.  For example, `QWheelEvent` is split as [&nbsp;`QWheel`, `Event`&nbsp;] whereas Ronin will split it as [&nbsp;`Q`, `Wheel`, `Event`&nbsp;].

So, Ronin's performance may be better than the pure numbers imply.  However, without checking every Ludiso case and manually reinterpreting the splits, we can't say for sure.  All that aside, Ronin definitely gets many cases wrong.


⚙️ Other splitters in Spiral
----------------------------

Here is a list of all the splitters implemented in Spiral at this time:

| Splitter name          | Operation                                                                                                               |
|------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `delimiter_split`      | split only at characters `$` `~` `_` `.` `:` `/` `@`                                                                    |
| `digit_split`          | split only at digits                                                                                                    |
| `pure_camelcase_split` | split at forward camel case transitions (lower to upper case)                                                           |
| `safe_simple_split`    | split at hard delimiter characters and forward camel case only; won't split strings that don't follow strict camel case |
| `simple_split`         | split at hard delimiter characters and forward camel case, even if a string doesn't follow strict camel case conventions |
| `elementary_split`     | split by hard delimiters, forward camel case, and digits                                                                |
| `heuristic_split`      | split by hard delimiters, forward camel case, and digits, but recognize special cases such as `utf8`, `sha256`, etc.    |
| Samurai                | frequency-based algorithm published in the literature                                                                   |
| Ronin                  | frequency-based algorithm based on Samurai but greatly extended (see [next section](#-performance))                     |

The following table illustrates the differences between the simpler splitters.

| Input string   | pure camel  | safe simple| simple      | elementary   | heuristic  |
|----------------|-------------|------------|-------------|--------------|------------|
| `alllower`     | `alllower`  | `alllower`  | `alllower`  | `alllower`  | `alllower` |
| `ALLUPPER`     | `ALLUPPER`  | `ALLUPPER`  | `ALLUPPER`  | `ALLUPPER`  | `ALLUPPER` |
| `a_delimiter`  | `a_delimiter`  | `a` `delimiter`  | `a` `delimiter`  | `a` `delimiter`  | `a` `delimiter` |
| `a.delimiter`  | `a.delimiter`  | `a` `delimiter`  | `a` `delimiter`  | `a` `delimiter`  | `a` `delimiter` |
| `a$delimiter`  | `a$delimiter`  | `a` `delimiter`  | `a` `delimiter`  | `a` `delimiter`  | `a` `delimiter` |
| `a:delimiter`  | `a:delimiter`  | `a` `delimiter`  | `a` `delimiter`  | `a` `delimiter`  | `a` `delimiter` |
| `a_fooBar`     | `a_foo` `Bar`  | `a` `foo` `Bar`  | `a` `foo` `Bar`  | `a` `foo` `Bar`  | `a` `foo` `Bar` |
| `fooBar`       | `foo` `Bar`  | `foo` `Bar`  | `foo` `Bar`  | `foo` `Bar`  | `foo` `Bar` |
| `FooBar`       | `Foo` `Bar`  | `Foo` `Bar`  | `Foo` `Bar`  | `Foo` `Bar`  | `Foo` `Bar` |
| `Foobar`       | `Foobar`  | `Foobar`  | `Foobar`  | `Foobar`  | `Foobar` |
| `fooBAR`       | `foo` `BAR`  | `fooBAR`  | `foo` `BAR`  | `foo` `BAR`  | `foo` `BAR` |
| `fooBARbif`    | `foo` `BARbif`  | `fooBARbif`  | `foo` `BARbif`  | `foo` `BARbif`  | `foo` `BARbif` |
| `fooBARzBif`   | `foo` `BARz` `Bif`  | `fooBARzBif`  | `foo` `BARz` `Bif`  | `foo` `BARz` `Bif`  | `foo` `BARz` `Bif` |
| `ABCfoo`       | `ABCfoo`  | `ABCfoo`  | `ABCfoo`  | `ABCfoo`  | `ABCfoo` |
| `ABCFoo`       | `ABCFoo`  | `ABCFoo`  | `ABCFoo`  | `ABCFoo`  | `ABCFoo` |
| `ABCFooBar`    | `ABCFoo` `Bar`  | `ABCFooBar`  | `ABCFoo` `Bar`  | `ABCFoo` `Bar`  | `ABCFoo` `Bar` |
| `ABCfooBar`    | `ABCfoo` `Bar`  | `ABCfooBar`  | `ABCfoo` `Bar`  | `ABCfoo` `Bar`  | `ABCfoo` `Bar` |
| `fooBar2day`   | `foo` `Bar2day`  | `foo` `Bar2day`  | `foo` `Bar2day`  | `foo` `Bar` `2` `day`  | `foo` `Bar` `2` `day` |
| `fooBar2Day`   | `foo` `Bar2Day`  | `foo` `Bar2Day`  | `foo` `Bar2Day`  | `foo` `Bar` `2` `Day`  | `foo` `Bar` `2` `Day` |
| `fooBAR2day`   | `foo` `BAR2day`  | `fooBAR2day`  | `foo` `BAR2day`  | `foo` `BAR` `2` `day`  | `foo` `BAR` `2` `day` |
| `fooBAR2Day`   | `foo` `BAR2Day`  | `fooBAR2Day`  | `foo` `BAR2Day`  | `foo` `BAR` `2` `Day`  | `foo` `BAR` `2` `Day` |
| `foo3000`      | `foo3000`  | `foo3000`  | `foo3000`  | `foo` `3000`  | `foo` `3000` |
| `99foo3000`    | `99foo3000`  | `99foo3000`  | `99foo3000`  | `99` `foo` `3000`  | `99` `foo` `3000` |
| `foo2Bar`      | `foo2Bar`  | `foo2Bar`  | `foo2Bar`  | `foo` `2` `Bar`  | `foo` `2` `Bar` |
| `foo2bar2`     | `foo2bar2`  | `foo2bar2`  | `foo2bar2`  | `foo` `2` `bar` `2`  | `foo` `2` `bar` `2` |
| `Foo2Bar2`     | `Foo2Bar2`  | `Foo2Bar2`  | `Foo2Bar2`  | `Foo` `2` `Bar` `2`  | `Foo` `2` `Bar` `2` |
| `MyInt32`      | `My` `Int32`  | `My` `Int32`  | `My` `Int32`  | `My` `Int` `32`  | `My` `Int32` |
| `MyInt42`      | `My` `Int42`  | `My` `Int42`  | `My` `Int42`  | `My` `Int` `42`  | `My` `Int` `42` |
| `MyInt32Var`   | `My` `Int32Var`  | `My` `Int32Var`  | `My` `Int32Var`  | `My` `Int` `32` `Var`  | `My` `Int32` `Var` |
| `2ndvar`       | `2ndvar`  | `2ndvar`  | `2ndvar`  | `2` `ndvar`  | `2nd` `var` |
| `the2ndvar`    | `the2ndvar`  | `the2ndvar`  | `the2ndvar`  | `the` `2` `ndvar`  | `the` `2nd` `var` |
| `the2ndVar`    | `the2nd` `Var`  | `the2nd` `Var`  | `the2nd` `Var`  | `the` `2` `nd` `Var`  | `the` `2nd` `Var` |
| `row10`        | `row10`  | `row10`  | `row10`  | `row` `10`  | `row` `10` |
| `utf8`         | `utf8`  | `utf8`  | `utf8`  | `utf` `8`  | `utf8` |
| `aUTF8var`     | `a` `UTF8var`  | `aUTF8var`  | `a` `UTF8var`  | `a` `UTF` `8` `var`  | `a` `UTF8` `var` |
| `J2SE4me`      | `J2SE4me`  | `J2SE4me`  | `J2SE4me`  | `J` `2` `SE` `4` `me`  | `J2SE` `4` `me` |
| `IPv4addr`     | `IPv4addr`  | `IPv4addr`  | `IPv4addr`  | `IPv` `4` `addr`  | `IPv4` `addr` |

Ronin and Samurai are more advanced than any of the simple splitters above.  Ronin in particular does everything `heuristic_splitter` does, but handles far more difficult cases.

⚠️ Limitations
--------------

Ronin is the most advanced splitter in the Spiral package, but it is not perfect by any means.  Certain limitations are known:

* Ronin is tuned for splitting program identifiers, which is _not_ the same as splitting strings of concatenated words.  With its default parameter values, it is not good at splitting strings like `driveourtrucks` which are not composed of tokens commonly encountered in source code contexts.  (By the way, reducing the value of parameter `low_freq_cutoff` in `ronin.init()` to something like `10` makes Ronin more likely to split concatenated word strings like `driveourtrucks` or `societynamebank`. However, this comes at the expense of worsening scores on the INTT and Ludiso data sets.)

* Ronin was trained on source code repositories containing Python code.  The default frequency table may not be optimal for splitting things that come from non-Python source files, although the test results on Ludiso and INTT show that it is pretty good on non-Python content.

* Spiral includes a set of predefined special terms in the file [`constants.py`](spiral/constants.py) so that `heuristic_split` and the Ronin splitter can recognize certain character sequences that should be treated as units.  Examples include `utf8`, `ipv4`, `checkbox`, `J2SE` and others.  The use of specialized dictionaries like this is an approach taken in other splitters (including Simon Butler's [INTT](https://github.com/sjbutler/intt)) and is the only known way to prevent incorrect splits of special terms, but it is also an obvious limitation: the list is surely incomplete (and can never _be_ complete because new terms are invented all the time), and may even cause incorrect splits in some contexts.

* The current algorithm implemented in Ronin arose organically after a lot of trial-and-error experimentation, and as a consequence, is rather gnarly and difficult to explain.  The implementation could be made more efficient and the algorithm clarified by a nice about of refactoring. 


📚 More information
-----------------

The name "Ronin" is a play on the use of the name "Samurai" by Enslen et al. (2009) for their identifier splitting algorithm.  The core loop of Ronin is based on Samurai, but it would be inappropriate to call this implementation Samurai too.  In an effort to imply the lineage of this modified algorithm, I chose "Ronin" (a name referring to a drifter samurai without a master, during the Japanese feudal period).

I implemented Samurai based on the description of the algorithm published in the following paper, then modified it repeatedly in an attempt to improve performance.  Ronin is the result.  A goal for Ronin was to produce a splitter that had good performance even without using a local frequency table.

<details>
<summary><a href="https://dl.acm.org/citation.cfm?id=1591139">
Enslen, E., Hill, E., Pollock, L., & Vijay-Shanker, K. (2009). Mining source code to automatically split identifiers for software analysis. In Proceedings of the 6th IEEE International Working Conference on Mining Software Repositories (MSR'09)</a></summary><br>
<em>
Abstract: Automated software engineering tools (e.g., program search, concern location, code reuse, quality assessment, etc.)  increasingly rely on natural language information from comments and identifiers in code.  The first step in analyzing words from identifiers requires splitting identifiers into their constituent words. Unlike natural languages, where space and punctuation are used to delineate words, identifiers cannot contain spaces.  One common way to split identifiers is to follow programming language naming conventions. For example, Java programmers often use camel case, where words are delineated by uppercase letters or non-alphabetic characters.  However, programmers also create identifiers by concatenating sequences of words together with no discernible delineation, which poses challenges to automatic identifier splitting. In this paper, we present an algorithm to automatically split identifiers into sequences of words by mining word frequencies in source code.  With these word frequencies, our identifier splitter uses a scoring technique to automatically select the most appropriate partitioning for an identifier. In an evaluation of over 8000 identifiers from open source Java programs, our Samurai approach outperforms the existing state of the art techniques.
</em>
</details>
<br>

The Ludiso data set is described in the following paper:

<details>
<summary><a href="https://link.springer.com/article/10.1007/s10664-013-9261-0">
Hill, E., Binkley, D., Lawrie, D., Pollock, L., & Vijay-Shanker, K. (2014). An empirical study of identifier splitting techniques. Empirical Software Engineering, 19(6), 1754–1780.</a></summary><br>
<em>Abstract: Researchers have shown that program analyses that drive software development and maintenance tools supporting search, traceability and other tasks can benefit from leveraging the natural language information found in identifiers and comments. Accurate natural language information depends on correctly splitting the identifiers into their component words and abbreviations. While conventions such as camel-casing can ease this task, conventions are not well-defined in certain situations and may be modified to improve readability, thus making automatic splitting more challenging. This paper describes an empirical study of state-of-the-art identifier splitting techniques and the construction of a publicly available oracle to evaluate identifier splitting algorithms. In addition to comparing current approaches, the results help to guide future development and evaluation of improved identifier splitting approaches.
</em>
</details>
<br>

The INTT splitter and data set are described in the following paper:

<details>
<summary><a href="https://link.springer.com/chapter/10.1007%2F978-3-642-22655-7_7">
Butler, S., Wermelinger, M., Yu, Y., & Sharp, H. (2011). Improving the Tokenisation of Identifier Names. In ECOOP 2011 – Object-Oriented Programming (pp. 130–154). Springer, Berlin, Heidelberg.
</a></summary><br>
<em>
Abstract: Identifier names are the main vehicle for semantic information during program comprehension. Identifier names are tokenised into their semantic constituents by tools supporting program comprehension tasks, including concept location and requirements traceability. We present an approach to the automated tokenisation of identifier names that improves on existing techniques in two ways. First, it improves tokenisation accuracy for identifier names of a single case and those containing digits. Second, performance gains over existing techniques are achieved using smaller oracles. Accuracy was evaluated by comparing the output of our algorithm to manual tokenisations of 28,000 identifier names drawn from 60 open source Java projects totalling 16.5 MSLOC. We also undertook a study of the typographical features of identifier names (single case, use of digits, etc.) per object-oriented construct (class names, method names, etc.), thus providing an insight into naming conventions in industrial-scale object-oriented code. Our tokenisation tool and datasets are publicly available.
</em>
</details>



⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/casics/spiral/issues) for this repository.

♬ Contributing &mdash; info for developers
------------------------------------------

A lot remains to be done on CASICS in many areas.  We would be happy to receive your help and participation if you are interested.  Please feel free to contact the developers either via GitHub or the mailing list [casics-team@googlegroups.com](casics-team@googlegroups.com).

Everyone is asked to read and respect the [code of conduct](CONDUCT.md) when participating in this project.

❤️ Acknowledgments
------------------

Funding for this and other CASICS work has come from the [National Science Foundation](https://nsf.gov) via grant NSF EAGER #1533792 (Principal Investigator: Michael Hucka) to the California Institute of Technology.

The installation of Spiral includes a dictionary containing words from the [NTLK](https://github.com/nltk) project, specifically the `words` and `wordnet` dictionaries.  The `word` dictionary is public domain, but the `wordnet` dictionary is copyright 2006 by Princeton University and made available under [license terms](https://wordnet.princeton.edu/license-and-commercial-use) that permit free redistribution.

The vector artwork of the segmented spiral illusion at the top of this page was obtained from [www.123freevectors.com](www.123freevectors.com).
    
<div align="center">
  <a href="https://www.nsf.gov">
    <img width="105" height="105" src=".graphics/NSF.svg">
  </a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
