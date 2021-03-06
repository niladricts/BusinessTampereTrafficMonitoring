# BusinessTampereTrafficMonitoring
This Project will be done as part of Software Engineering Course by Tampere University. The aim of this project to build a Machine Learning module to detect objects by parsing traffic camera feeds and show the data like average wait time, average queue length at traffic for different vehicles.

Currently the only implemented feature is counting how many cars are left after a light turns red (when there is not enough green light time).


## Development setup
1. Make sure you have a non-ancient Python (I think the tox config should work with Python 3.9 and Python 3.10, but I've only tested with 3.9)
1. Create a virtual environment (on Linux I use `python -m venv .venv` to do this)
1. Activate virtual environment (on Linux I use `. .venv/bin/activate` to do this)
1. Install the package and its dependencies inside the virtual environment (`pip install .`) – if the installation completed successfully the system should now be ready to run
1. Install dependencies required for development (tox, pytest, and various linters) (`pip install -r requirements-dev.txt`)
1. Now you can run tests and linters from command line using `tox` (runs everything listed in variable `envlist` in file `tox.ini` by default, or you can select specific ones like `tox -e pylint` or `tox -e flake8`)
