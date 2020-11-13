Testing
=======

Sportsipy contains a testing suite which aims to test all major portions
of code for proper functionality. To run the test suite against your
environment, ensure all of the requirements are installed by running::

    pip install -r requirements.txt

Next, start the tests by running py.test while optionally including coverage
flags which identify the amount of production code covered by the testing
framework::

    py.test --cov=sportsipy --cov-report term-missing tests/

If the tests were successful, it will return a green line will show a message at
the end of the output similar to the following::

    ======================= 380 passed in 245.56 seconds =======================

If a test failed, it will show the number of failed and what went wrong within
the test output. If that's the case, ensure you have the latest version of code
and are in a supported environment. Otherwise, create an issue on GitHub to
attempt to get the issue resolved.
