
# Plates Generator
This module generates a list of source and destination plates according to the set of samples to test.

## Running from the CLI
~~~bash
python -m icfree.plates_generator \
  <cfps-parameters tsv file> \
  <sampling csv|tsv file>
~~~

## Options
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

## Example
~~~bash
python -m icfree.plates_generator \
  tests/data/plates_generator/input/proCFPS_parametersB3.tsv \
  tests/data/plates_generator/input/sampling.csv \
  -v 1000 \
  -of out
~~~

## Output
The output files are:
<ul>
<li><code>source_plate.json</code>: describe the source plate(s)</li>
<li><code>destination_plate.json</code>: describe the destination plate(s)</li>
<li><code>volumes_summary.tsv</code>: contains the summary of parameters volumes</li>
</ul>

# Help
Display help by running:
~~~bash
python -m icfree.plates_generator --help
~~~

# Authors
Joan Hérisson, Yorgo EL MOUBAYED

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
