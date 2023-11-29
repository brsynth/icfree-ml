
# Converter
The `plates_generator` module works with volume values as input. This `converter` module converts concentration values into volume values.

## Running from the CLI
~~~bash
python -m icfree.converter <parameters_file.tsv> <concentrations_file.tsv>
~~~

## Positional arguments
<ul>
<li><code>parameters_file.tsv</code>: File containing informations (maximum value, stock conentration, dead volumes, ratios) on parameters to convert concentrations. An example can be find here: [tests/data/converter/input/proCFPS_parameters.tsv](proCFPS_parameters.tsv)</li>
<li><code>concentrations_file.tsv</code>: Output folder to write output files (default: working dir)</li>
</ul>

## Optional arguments
<ul>
<li><code>-v</code> or <code>--sample_volume</code>: Final sample volume in each well in nL (default: 1000)</li>
<li><code>-of</code>, --output-folder: Output folder to write output files (default: working dir)</li>
</ul>

## Example
~~~bash
python -m icfree.converter \
  tests/data/converter/input/proCFPS_parameters.tsv \
  tests/data/converter/input/sampling_concentrations.tsv \
  -of out
~~~

## Input file

Below is an example of an input file:

| Parameter    | maxValue | stockConcentration  | deadVolume | Ratios              |
|--------------|----------|---------------------|------------|---------------------|
| Mg-glutamate | 4        | 168                 | 0          | 0.0 0.1 0.3 0.5 1.0 |
| k-glutamate  | 80       | 3360                | 0          |                     |
| CoA          | 0.26     | 210                 | 0          |                     |
| 3-PGA        | 30       | 1400                | 0          |                     |
| NTP          | 1.5      | 630                 | 0          |                     |
| NAD          | 0.33     | 138.6               | 0          |                     |
| Folinic acid | 0.068    | 28.56               | 0          |                     |
| Spermidine   | 1        | 420                 | 0          |                     |
| tRNA         | 0.2      | 84                  | 0          |                     |
| Amino acids  | 1.5      | 6                   | 0          |                     |
| CAMP         | 0.75     | 200                 | 0          |                     |
| Extract      | 30       | 300                 | 2000       | 1                   |
| HEPES        | 50       | 2100                | 0          | 1                   |
| PEG          | 2        | 200                 | 4000       | 1                   |
| Promoter     | 10       | 300                 | 0          | 1                   |
| RBS          | 10       | 200                 | 0          | 1                   |

The first column is the parameter (or factor) names.

The second column is the maxValue of the parameter that will be used in the sampling.

The third column is the concnetration of the stock.

The fourth column is the deadVolume of the parameter. This is used to calculate the volume of the parameter that will not be pipetted by the robot (because of viscosity).

The fifth column is the specific ratios we want to have for this parameter. If nothing defined, then take ratios given in program options. If one single number is given, then take this number as a const value.

## Output
The output file is:
<ul>
<li><code>volumes.csv</code>: contains the volume values</li>
</ul>

# Help
Display help by running:
~~~bash
python -m icfree.converter --help
~~~

# Authors
Joan Hérisson, Yorgo EL MOUBAYED

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
