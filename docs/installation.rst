Installation
============

Requirements
------------

The Chat Console requires Qt, such as
`PyQt5 <http://www.riverbankcomputing.com/software/pyqt/intro>`_,
`PyQt4 <https://www.riverbankcomputing.com/software/pyqt/download>`_,
or `PySide <http://pyside.github.io/docs/pyside>`_.

Although `pip <https://pypi.python.org/pypi/pip>`_ and
`conda <http://conda.pydata.org/docs>`_ may be used to install the console, conda
is simpler to use since it automatically installs PyQt. Alternatively,
the console installation with pip needs additional steps since pip cannot install
the requirement.

Install using conda
-------------------

To install::

    conda install chconsole

**Note:** If the console is installed using conda, it will **automatically**
install the Qt requirement as well.

Install using pip
-----------------

To install::

    pip install chconsole

**Note:** Make sure that Qt is installed. Unfortunately, Qt cannot be
installed using pip. The next section gives instructions on installing Qt.

Installing Qt (if needed)
-------------------------

We recommend installing PyQt with `conda <http://conda.pydata.org/docs>`_::

    conda install pyqt

or with a system package manager. For Windows, PyQt binary packages may be
used.
