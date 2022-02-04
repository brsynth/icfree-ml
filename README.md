
# Description

Design of experiments (DoE) and machine learning scripts for the iCFree project

# Installation

~~~bash
git clone https://github.com/brsynth/icfree-ml.git
~~~

~~~bash
cd icfree-ml
~~~

~~~bash
bash packages.sh
~~~

# Usage

Running the initial_set_generator module

~~~bash
python -m initial_set_generator <tsv parameters file>
~~~

Running the robots_handler module

~~~bash
python -m robots_handler < initial_training_set tsv file> < normalizer_set tsv file> <autofluorescence tsv file>
~~~

# Authors

Yorgo EL MOUBAYED

# License

Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
