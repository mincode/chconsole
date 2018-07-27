# Chat Console -- MathChat System

[![Build Status](https://travis-ci.org/jupyter/qtconsole.svg?branch=master)](https://travis-ci.org/jupyter/qtconsole)
[![Documentation Status](https://readthedocs.org/projects/chconsole/badge/?version=stable)](http://chconsole.readthedocs.org/en/stable/)

Chat Console, part of the MathChat system for collaborative computational mathematics, is a command console (shell) for Jupyter kernels, with enhancements for inline graphics,
syntax highlighting, and much more.
It facilitates collaborative
work by supporting chat and displaying commands of multiple users asynchronously.

![qtconsole](docs/_static/example_dialog.png)

**Note:** Make sure that Qt is installed. Unfortunately, Qt cannot be
installed using pip. The next section gives instructions on installing Qt.

## Install Chat Console

The Chat Console requires Qt, such as
[PyQt5](http://www.riverbankcomputing.com/software/pyqt/intro),
[PyQt4](https://www.riverbankcomputing.com/software/pyqt/download),
or [PySide](http://pyside.github.io/docs/pyside).

### Installing Qt (if needed)
We recommend installing PyQt with [conda](http://conda.pydata.org/docs):

    conda install pyqt

or with a system package manager. For Windows, PyQt binary packages may be
used.

### Install Chat Console using pip
To install:

    pip install chconsole


## Usage
To run the Chat Console:

    chconsole

or

    jupyter chconsole

Chat Console can either start its own IPython kernel or
attach to an independent Jupyter kernel, including
 IPython, through a connection file.
For convenience, a script to start an
independent Ipython kernel is included:

    chc-python

## Resources
- Documentation for the Chat Console
  * [latest version](http://chconsole.readthedocs.org/en/latest/)
  [[PDF](https://media.readthedocs.org/pdf/chconsole/latest/chconsole.pdf)]
  * [stable version](http://chconsole.readthedocs.org/en/stable/)
  [[PDF](https://media.readthedocs.org/pdf/chconsole/stable/chconsole.pdf)]
- [Project Jupyter website](https://jupyter.org)

## Acknowledgments

- Comcast Innovation Fund
- Seton Hall University
