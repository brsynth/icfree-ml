
# Plates Generator

This module generates a list of source and destination plates according to the set of volume samples to test.

<!-- resize and center image -->
<p align="center">
<img src="/img/plates_generator.png" width="500">
</p>

### Running from the CLI
~~~bash
python -m icfree.plates_generator \
  <parameters.tsv>
  -v <sample_volume>
~~~

### Positional arguments
* [sampling.tsv](/tests/data/plates_generator/input/sampling.csv): File containing volumes to test.
* <code>-v</code>, <code>--sample_volume</code>: Final sample volume in each well in nL.

### Options
<ul>
  <li><code>-sdv</code>, <code>--src-plt-dead-volume</code>: dead volume to add in the source plate in nL (default: 15000)</li>
  <li><code>-ssw</code>, <code>--src-start-well</code>: Starter well of source plate to begin filling the 384 well-plate. (default: 'A1')</li>
  <li><code>-spd</code>, <code>--src-plt-dim</code>: Dimensions of source plate(s). (default: '16x24')</li>
  <li><code>-spwc</code>, <code>--src-plt-well-capacity</code>: Maximum volume capacity of the source plate(s) in nL (default: 60000)</li>
  <li><code>-ncc</code>, <code>--new-col-comp</code>: List of components for which the filling will start at a new column in the source plate.</li>
  <li><code>-dsw</code>, <code>--dst-start-well</code>: Starter well of destination plate to begin filling the 384 well-plate. (default: 'A1')</li>
  <li><code>-dpd</code>, <code>--dst-plt-dim</code>: Dimensions of destination plate(s). (default: '16x24')</li>
  <li><code>-dpwc</code>, <code>--dst-plt-well-capacity</code>: Maximum volume capacity of the destination plate(s) in nL (default: 60000)</li>
  <li><code>--nplicates</code>: Numbers of copies of volume sets (default: 1)</li>
  <li><code>-ofmt</code> {csv,tsv}, --output-format {csv,tsv}: Output file format for wells file (default: csv)</li>
</ul>


### Example
~~~bash
python -m icfree.plates_generator \
  tests/data/plates_generator/input/sampling.csv \
  -v 1000
~~~

### Output
The output files are:

* [source_plate.csv](/tests/data/plates_generator/output/source_plate_1.csv): source plate 1 volumes
* [destination_plate.csv](/tests/data/plates_generator/output/destination_plate_1.csv): destination plate 1 volumes

### Help
Display help by running:
~~~bash
python -m icfree.plates_generator --help
~~~

### Authors
Joan Hérisson (with help of ChatGPT-4)

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
