
# Description

Design of experiments (DoE) and machine learning packages for the iCFree project

# Installation

~~~bash
git clone https://github.com/brsynth/icfree-ml.git
~~~

~~~bash
cd icfree-ml
~~~

~~~bash
conda env create -f environment.yaml
~~~

~~~bash
conda activate icfree
~~~

# Usage

Running plates_generator from the CLI

~~~bash
python -m icfree.plates_generator <cfps-parameters tsv file> -of <output_folder>
~~~

Running echo_instructor from the CLI

~~~bash
python -m icfree.echo_instructor 
<cfps-parameters tsv file> \ 
<initial_training_set tsv file> \ 
<normalizer_set tsv file> \ 
<autofluorescence_set tsv file> \ 
-v <sample_volume> \
-of <output_folder>
~~~

# Help

Display help by running:
~~~bash
python -m icfree.plates_generator --help
~~~

~~~bash
python -m icfree.echo_instructor --help
~~~

# Authors

Yorgo EL MOUBAYED, Joan Hérisson

# License

Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
