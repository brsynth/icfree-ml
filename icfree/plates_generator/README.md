
# Plates Generator

This module generates a list of source and destination plates according to the set of volume samples to test.

<!-- resize and center image -->
<p align="center">
<img src="/img/plates_generator.png" width="500">
</p>

### Running from the CLI
~~~bash
python -m icfree.plates_generator \
  <parameters.tsv> \
  <vol_sampling.[csv|tsv]>
~~~

### Positional arguments
* [parameters.tsv](/tests/data/plates_generator/input/parameters.tsv): File containing informations (maximum value, stock conentration, dead volumes, ratios) on parameters
  * The first column is the parameter (or factor) names.
  * The second column is the maximum value of the parameter that will be used in the sampling.
  * The third column is the concentration of the stock.
  * The fourth column is the dead volume of the parameter. This is used to calculate the volume of the parameter that will not be pipetted by the robot (because of viscosity).
  * The fifth column is the specific ratios we want to have for this parameter. If nothing defined, then take ratios given in program options. If one single number is given, then take this number as a const value.

* [sampling.tsv](/tests/data/plates_generator/input/sampling.tsv): File containing volumes to test

### Options
<ul>
  <li><code>-v</code>, <code>--sample_volume</code>: Final sample volume in each well in nL (default: 10000)</li>
  <li><code>-sdv</code>, <code>--source_plate_dead_volume</code>: deadVolume to add in the source plate in nL (default: 15000)</li>
  <li><code>-ddv</code>, <code>--dest_plate_dead_volume</code>: deadVolume to add in the dest plate in nL (default: 15000)</li>
  <li><code>-dsw</code>, <code>--dest-starting_well</code>: Starter well of destination plate to begin filling the 384 well-plate. (default: A1)</li>
  <li><code>-ssw</code>, <code>--src-starting_well</code>: Starter well of source plate to begin filling the 384 well-plate. (default: A1)</li>
  <li><code>-of</code>, --output-folder: Output folder to write output files (default: working dir)</li>
  <li><code>-ofmt</code> {csv,tsv}, --output-format {csv,tsv}: Output file format for wells file (default: csv)</li>
  <li><code>--nplicate</code>: Numbers of copies of volume sets (default: 3)</li>
  <li><code>--keep-nil-vol</code>: Keep nil volumes in instructions or not (default: yes)</li>
  <li><code>-spwc</code>, <code>--source_plate_well_capacity</code>: Maximum volume capacity of the source plate in nL (default: 60000)</li>
  <li><code>-dpwc</code>, <code>--dest_plate_well_capacity</code>: Maximum volume capacity of the dest plate in nL (default: 60000)</li>
  <li><code>--optimize-well-volumes</code>: Save volumes in source plate for all factors. It may trigger more volume pipetting warnings. If list of factors is given (separated by blanks), save: only for these ones (default: <code>[]</code>).</li>
  <li><code>--plate-dimensions</code>: Dimensions of plate separated by a 'x', e.g. <code>nb_rows x nb_cols</code> (default: 16x24).
</ul>


### Example
~~~bash
python -m icfree.plates_generator \
  tests/data/plates_generator/input/parameters.tsv \
  tests/data/plates_generator/input/sampling.tsv \
  -v 1000 \
  -of out
~~~

### Output
The output files are:

* [source_plate.json](/tests/data/plates_generator/output/source_plate_1.json): describe the source plate 1
* [source_plate.csv](/tests/data/plates_generator/output/source_plate_1.csv): source plate 1 volumes
* [destination_plate.json](/tests/data/plates_generator/output/destination_plate_1.json): describe the destination plate 1
* [destination_plate.csv](/tests/data/plates_generator/output/destination_plate_1.csv): destination plate 1 volumes
* [volumes_summary.tsv](/tests/data/plates_generator/output/plate_volumes_summary.json): contains the summary of parameters volumes

### Help
Display help by running:
~~~bash
python -m icfree.plates_generator --help
~~~

### Authors
Joan Hérisson

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
