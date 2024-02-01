[![Tests](https://github.com/brsynth/icfree-ml/actions/workflows/test.yml/badge.svg)](https://github.com/brsynth/icfree-ml/actions/workflows/test.yml)

# Description

Design of experiments (DoE) and machine learning packages for the iCFree project

![icfree](/img/icfree.png)

# Requirements

Python 3.8+

# Installation

~~~bash
conda env create -n <env_name> icfree
conda activate <env_name>
~~~

# Usage
iCFree is a package and is only runnable through the modules below.

## Sampler
This module generates a list of values for all parameters given in the input file. The values are generated using a Latin Hypercube Sampling (LHS) method. The number of values generated is given by the user and the values are saved in csv or tsv file.

The LHS values are generated using the `lhs` function from the `pyDOE` package and binned into bins to reduce the combinatorial space.

Documentation can be found in [icfree/sampler/README.md](icfree/sampler/README.md) file.

## Converter
The `plates_generator` module works with volume values as input. This `converter` module converts concentration values into volume values.

Documentation can be found in [icfree/converter/README.md](icfree/converter/README.md) file.


## Plates Generator
This module generates a list of source and destination plates according to the set of samples to test.

Documentation can be found in [icfree/plates_generator/README.md](icfree/plates_generator/README.md) file.

## Instructor
The module generates a list of instructions to perform the experiment.

Documentation can be found in [icfree/instructor/README.md](icfree/instructor/README.md) file.

# Help
Display help by running:
~~~bash
python -m icfree.<module> --help
~~~

# Authors
Joan Hérisson, Yorgo EL MOUBAYED

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
