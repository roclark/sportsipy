Installation
============

The easiest way to install `sportsipy` is by downloading the latest
released binary from PyPI using PIP. For instructions on installing PIP, visit
`PyPA.io <https://pip.pypa.io/en/stable/installing/>`_ for detailed steps on
installing the package manager for your local environment.

Next, run::

    pip install sportsipy

to download and install the latest official release of `sportsipy` on
your machine. You now have the latest stable version of `sportsipy`
installed and can begin using it following the examples!

If the bleeding-edge version of `sportsipy` is desired, clone this
repository using git and install all of the package requirements with PIP::

    git clone https://github.com/roclark/sportsipy
    cd sportsipy
    pip install -r requirements.txt

Once complete, create a Python wheel for your default version of Python by
running the following command::

    python setup.py sdist bdist_wheel

This will create a `.whl` file in the `dist` directory which can be installed
with the following command::

    pip install dist/*.whl
