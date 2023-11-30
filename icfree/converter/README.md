
# Converter
<!-- resize and center image -->
<p align="center">
<img src="/img/converter.png" width="400">
</p>

The `plates_generator` module works with volume values as input. This `converter` module converts concentration values into volume values.

### Running from the CLI
~~~bash
python -m icfree.converter <parameters_file.tsv> <concentrations_file.tsv>
~~~

### Positional arguments
<ul>
<li><code>parameters_file.tsv</code>: File containing informations (maximum value, stock conentration, dead volumes, ratios) on parameters to convert concentrations</li>
<li><code>concentrations_file.tsv</code>: File containing concentrations to convert</li>
</ul>

Examples can be found here:

* [concentrations.tsv](/tests/data/converter/input/sampling_concentrations.tsv)

* [parameters.tsv](/tests/data/converter/input/parameters.tsv)

  * The first column is the parameter (or factor) names.
  * The second column is the maximum value of the parameter that will be used in the sampling.
  * The third column is the concentration of the stock.
  * The fourth column is the dead volume of the parameter. This is used to calculate the volume of the parameter that will not be pipetted by the robot (because of viscosity).
  * The fifth column is the specific ratios we want to have for this parameter. If nothing defined, then take ratios given in program options. If one single number is given, then take this number as a const value.

### Optional arguments
<ul>
<li><code>-v</code> or <code>--sample_volume</code>: Final sample volume in each well in nL (default: 1000)</li>
<li><code>-of</code>, --output-folder: Output folder to write output files (default: working dir)</li>
</ul>

### Example
~~~bash
python -m icfree.converter \
  tests/data/converter/input/parameters.tsv \
  tests/data/converter/input/sampling_concentrations.tsv \
  -of out
~~~

The output file contains the volumes and can be found here: [volumes.tsv](/tests/data/converter/output/sampling_volumes.tsv)

### Help
Display help by running:
~~~bash
python -m icfree.converter --help
~~~

### Authors
Joan Hérisson

### License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
