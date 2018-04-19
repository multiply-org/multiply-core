<img alt="MULTIPLY" align="right" src="https://raw.githubusercontent.com/multiply-org/multiply-core/master/doc/source/_static/logo/Multiply_multicolour.png" />

# MULTIPLY Prior Engine

[![Build Status](https://travis-ci.org/multiply-org/prior-engine.svg?branch=master)](https://travis-ci.org/multiply-org/prior-engine)
[![Documentation Status](https://readthedocs.org/projects/multiply/badge/?version=latest)](http://multiply.readthedocs.io/en/latest/?badge=latest)
                
<!-- [![Documentation Status](https://readthedocs.org/projects/prior-engine/badge/?version=latest)](http://prior-engine.readthedocs.io/en/latest/?badge=latest) -->

This repository contains the prior engine for the MULTIPLY main platform.
It provides *a priori* information to the [Inference Engine](https://github.com/multiply-org/KaFKA-InferenceEngine) to support land surface parameter retrieval.
The documentation is part of the MULTIPLY core documentation on [ReadTheDocs](http://multiply.readthedocs.io/en/latest/). 
<!-- Add plans and current status? -->

## Contents

* `aux_data/` Auxiliary data for prior generation.
* `doc` - The auto generated documentation of all prior engine classes and function definitions. 
* `multiply_prior-engine/` - The main prior engine software package.
as source of information and orientation.
* `recipe` Conda installation recipe.
* `test/` - The test package.
* `setup.py` - main build script, to be run with Python 3.6
* `LICENSE.md` - License of software in repository.
<!-- * `helpers/` - Helper functions. -->

## How to install

The first step is to clone the latest code and step into the check out directory: 

    $ git clone https://github.com/multiply-org/prior-engine.git
    $ cd prior-engine
    
The MULTIPLY platform has been developed against Python 3.6. 
It cannot be guaranteed to work with previous Python versions.

The MULTIPLY prior engine can be run from sources directly.
To install the MULTIPLY prior engine into an existing Python environment just for the current user, use

    $ python setup.py install --user
    
To install the MULTIPLY Core for development and for the current user, use

    $ python setup.py develop --user

## Module requirements

- `python-dateutil`
- `gdal`
- `matplotlib`
- `numpy`
- `pyyaml`
- `shapely`
 

## How to use

MULTIPLY prior engine is available as Python Package. 
To import it into your python application, use

```python
import multiply_prior_engine
```
    
## Generating the Documentation

We use [Sphinx](http://www.sphinx-doc.org/en/stable/rest.html) to generate the documentation of the MULTIPLY platform on [ReadTheDocs](http://multiply.readthedocs.io/en/latest/). 

The source files of the main documentation of the MULTIPLY platform is to be found in the [MULTIPLY core repository](https://github.com/multiply-org/multiply-core).

If there is a need to build the *prior engine specific* docs locally, these additional software packages are required:

    $ conda install sphinx sphinx_rtd_theme mock
    $ conda install -c conda-forge sphinx-argparse
    $ pip install sphinx_autodoc_annotation

To regenerate the HTML docs, type    
    
    $ cd doc
    $ make html

## Authors

* **Joris Timmermans** - *Work on vegetation priors* 
* **Thomas Ramsauer** - *Work on soil priors* 

<!-- See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project. -->

## License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details

<!-- ## Acknowledgments -->

<!-- * Alexander Löw for.. -->

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/multiply-org/prior-engine/tags). 
