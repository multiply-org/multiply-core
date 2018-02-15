<img alt="MULTIPLY" align="right" src="https://raw.githubusercontent.com/multiply-org/multiply-core/master/doc/source/_static/logo/Multiply_multicolour.png" />


[![Build Status](https://travis-ci.org/multiply-org/multiply-core.svg?branch=master)](https://travis-ci.org/multiply-org/multiply-core)
                
# MULTIPLY Core

This repository contains core functions of the main platform.
It holds utility functions that are shared across the platform by several components as well as the documentation of
the complete platform.

## Contents

* `cli_example/` - An example for setting up a command line interface 
* `doc` - The main documentation of the MULTIPLY platform 
* `multiply_core/` - The main software package
* `multiply_dummy/` - A package with dummy code to display the function of the MULTIPLY platform. Deprecated, but kept 
as source of information and orientation.
* `test/` - The test package
* `setup.py` - main build script, to be run with Python 3.6

## How to install

The first step is to clone the latest code and step into the check out directory: 

    $ git clone https://github.com/multiply-org/multiply-core.git
    $ cd multiply-core
    
The MULTIPLY Core has been developed against Python 3.6. 
It cannot be guaranteed to work with previous Python versions.
The MULTIPLY Core can be run from sources directly.
To install the MULTIPLY Core into an existing Python environment just for the current user, use

    $ python setup.py install --user
    
To install the MULTIPLY Core for development and for the current user, use

    $ python setup.py develop --user

## How to use

MULTIPLY Core is available as Python Package. 
To import it into your python application, use

    $ import multiply_data_access
    
## Generating the Documentation

We use [Sphinx](http://www.sphinx-doc.org/en/stable/rest.html) to generate the documentation of the MULTIPLY platform 
on [ReadTheDocs](http://multiply.readthedocs.io/en/latest/). 
If there is a need to build the docs locally, these additional software packages are required:

    $ conda install sphinx sphinx_rtd_theme mock
    $ conda install -c conda-forge sphinx-argparse
    $ pip install sphinx_autodoc_annotation

To regenerate the HTML docs, type    
    
    $ cd doc
    $ make html

## License

