
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

# Sampler
This module generates a list of values for all parameters given in the input file. The values are generated using a Latin Hypercube Sampling (LHS) method. The number of values generated is given by the user and the values are saved in csv or tsv file.

The LHS values are generated using the `lhs` function from the `pyDOE` package and binned into bins to reduce the combinatorial space.

## Running from the CLI

~~~bash
python -m icfree.sampler <cfps-parameters tsv file>
~~~

## Options
<ul>
<li><code>-of</code> or <code>--output_folder</code>: path to the output folder where the generated plates will be saved (default: working dir)</li>
<li><code>--nb-sampling-steps</code>: Number of values for all factors when performing the sampling (default: 5)</li>
<li><code>--sampling-ratios</code>: Ratios for all factors when performing the sampling</li>
<li><code>--nb-samples</code>: Number of samples to generate for all factors when performing the sampling (default: 99)</li>
<li><code>--seed</code>: Seed to reproduce results (same seed number = same results)</li>
<li><code>--output-format</code>: Format of output file (default: csv)</li>
</ul>

## Example
~~~bash
python -m icfree.sampler tests/data/sampler/input/proCFPS_parametersB3.tsv -of out --nb-samples 100 --sampling-ratios 0.0 0.2 0.4 0.56 0.64 0.72 0.8 1.0 --output-format tsv
~~~

## Input file

Below is an example of an input file:
| **Parameter** 	| **maxValue** 	| **deadVolume** 	| **Ratios** 	|
|---------------	|------------	|---------------------------	|-------------------------	|---------------------------	|--------------------------	|
| Mg-glutamate  	| 4                         	| 0                         	| 0.0 0.1 0.3 0.5 1.0      	|
| k-glutamate   	| 80                        	| 0                         	|                          	|
| CoA           	| 0.26                      	| 0                         	|                          	|
| 3-PGA         	| 30                        	| 0                         	|                          	|
| NTP           	| 1.5                       	| 0                         	|                          	|
| NAD           	| 0.33                      	| 0                         	|                          	|
| Folinic acid  	| 0.068                     	| 0                         	|                          	|
| Spermidine    	| 1                         	| 0                         	|                          	|
| tRNA          	| 0.2                       	| 0                         	|                          	|
| Amino acids   	| 1.5                       	| 0                         	|                          	|
| CAMP          	| 0.75                      	| 0                         	|                          	|
| Extract       	| 30                        	| 2000                      	| 1.0                      	|
| HEPES         	| 50                        	| 0                         	| 1.0                      	|
| PEG           	| 2                         	| 4000                      	| 1.0                      	|
| Promoter      	| 10                        	| 0                         	| 1.0                      	|
| RBS           	| 10                        	| 0                         	| 1.0                      	|

The first column is the parameter (or factor) names.

The second column is the maxValue of the parameter that will be used in the sampling.

The third column is the deadVolume of the parameter. This is used to calculate the volume of the parameter that will not be pipetted by the robot (because of viscosity).

The fourth column is the specific ratios we want to have for this parameter. If nothing defined, then take ratios given in program options. If one single number is given, then take this number as a const value.

## Output
The output file is:
<ul>
<li><code>sampling.csv</code>: contains the sampling values</li>
</ul>


# Plates Generator
## Running from the CLI
This module generates a list of source and destination plates according to the set of samples to test.

~~~bash
python -m icfree.plates_generator <cfps-parameters tsv file> <sampling csv|tsv file>
~~~

## Options
<ul>
  <li><code>-v</code> SAMPLE_VOLUME, <code>--sample_volume</code> SAMPLE_VOLUME: Final sample volume in each well in nL (default: 10000)</li>
  <li><code>-sdv</code> SOURCE_PLATE_DEAD_VOLUME, <code>--source_plate_dead_volume</code> SOURCE_PLATE_DEAD_VOLUME: deadVolume to add in the source plate in nL (default: 15000)</li>
  <li><code>-ddv</code> DEST_PLATE_DEAD_VOLUME, <code>--dest_plate_dead_volume</code> DEST_PLATE_DEAD_VOLUME: deadVolume to add in the dest plate in nL (default: 15000)</li>
  <li><code>-dsw</code> DEST_STARTING_WELL, --dest-starting_well DEST_STARTING_WELL: Starter well of destination plate to begin filling the 384 well-plate. (default: A1)</li>
  <li><code>-ssw</code> SRC_STARTING_WELL, --src-starting_well SRC_STARTING_WELL: Starter well of source plate to begin filling the 384 well-plate. (default: A1)</li>
  <li><code>-of</code> OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER: Output folder to write output files (default: working dir)</li>
  <li><code>-ofmt</code> {csv,tsv}, --output-format {csv,tsv}: Output file format (default: csv)</li>
  <li><code>--nplicate</code> NPLICATE   Numbers of copies of volume sets (default: 3)</li>
  <li><code>--keep-nil-vol</code> KEEP_NIL_VOL: Keep nil volumes in instructions or not (default: yes)</li>
  <li><code>-spwc</code> SOURCE_PLATE_WELL_CAPACITY, <code>--source_plate_well_capacity</code> SOURCE_PLATE_WELL_CAPACITY: Maximum volume capacity of the source plate in nL (default: 60000)</li>
  <li><code>-dpwc</code> DEST_PLATE_WELL_CAPACITY, <code>--dest_plate_well_capacity</code> DEST_PLATE_WELL_CAPACITY: Maximum volume capacity of the dest plate in nL (default: 60000)</li>
  <li><code>--optimize-well-volumes</code> [OPTIMIZE_WELL_VOLUMES ...]: Save volumes in source plate for all factors. It may trigger more volume pipetting warnings. If list of factors is given (separated by blanks), save: only for these ones (default: <code>[]</code>).</li>
  <li><code>--plate-dimensions</code> PLATE_DIMENSIONS: Dimensions of plate separated by a 'x', e.g. <nb_rows>x<nb_cols>(default: 16x24).
</ul>

## Example
~~~bash
python -m icfree.plates_generator tests/data/plates_generator/input/proCFPS_parametersB3.tsv tests/data/plates_generator/input/sampling.csv -of out -v 1000
~~~

## Output
The output files are:
<ul>
<li><code>source_plate.json</code>: describe the source plate(s)</li>
<li><code>destination_plate.json</code>: describe the destination plate(s)</li>
<li><code>volumes_summary.tsv</code>: contains the summary of parameters volumes</li>
</ul>



# Instructor
## Running from the CLI
The module generates a list of instructions to perform the experiment.

~~~bash
python -m icfree.instructor 
--source_plates <source_plate file 1> <source_plate file 2>... \
--dest_plates <dest_plate file 1> <dest_plate file 2>... \
~~~

## Options
<ul>
  <li><code>-of</code> OUTPUT_FOLDER, <code>--output-folder</code> OUTPUT_FOLDER: Output folder to write output files (default: working dir)</li>
  <li><code>--robot</code> ROBOT: Robot name (default: echo)</li>
  <li><code>--source_plates</code> SOURCE_PLATES [SOURCE_PLATES ...]: Source plates files.</li>
  <li><code>--dest_plates</code> DEST_PLATES [DEST_PLATES ...]: Destination plates files.</li>
</ul>

## Example
~~~bash
python -m icfree.instructor --source_plates out/source_plate_1.json --dest_plates out/destination_plate_1.json -of out --robot echo
~~~

## Output
The output file is:
<ul>
<li><code>instructions.csv</code>: contains the instructions to perform the experiment</li>
<li><code>volumes_warning.csv</code>: contains the volumes that may cause issues with the choosen robot</li>
</ul>

# Help

Display help by running:
~~~bash
python -m icfree.<module> --help
~~~

# Authors

Joan Hérisson, Yorgo EL MOUBAYED

# License

Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
