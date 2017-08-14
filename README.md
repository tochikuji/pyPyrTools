# pyPyrTools: A multi-scale image processing tool

This is a fork of original pyPyrTools by LabForComputationalVision.
It provide a packaged and modern interface of original scripts,
and also contains some bug fixes.

For more details of this package (in practical), refer to original
README file (README.orig).

## Installation

Installation script has been implemented (in other words, it is packaged).

To install a package `pyrtools`, use `pip`
```
pip install . # . provides a project root of this package
```

or install with  `setup.py` manually,

```
python setup.py install
```

## Requirements

To install this package, some python packages are needed.
These installations will be done automatically if you use `pip`.

And this package contains native extensions with C.
C compilers (such as gcc) are needed to build them.

We note that, We didn't make any test even for an installation,
and we don't know how to use python in Windows environments...

## License
MIT
