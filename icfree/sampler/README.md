
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
python -m icfree.sampler \
  tests/data/sampler/input/proCFPS_parametersB3.tsv \
  --nb-samples 100 \
  --sampling-ratios 0.0 0.2 0.4 0.56 0.64 0.72 0.8 1.0 \
  --output-format tsv \
  -of out
~~~

## Input file

Below is an example of an input file:

|**Parameter**|**maxValue**|**deadVolume**|**Ratios**             |
|---------|--------|----------|-------------------|
|CP       |125     |0         |0.0 0.1 0.3 0.5 1.0|
|CPK      |125     |0         |1                  |
|tRNA     |125     |0         |                   |
|AA       |125     |0         |                   |
|ribosomes|125     |0         |                   |
|mRNA     |125     |0         |                   |
|Mg       |125     |0         |                   |
|K        |125     |0         |                   |

The first column is the parameter (or factor) names.

The second column is the maxValue of the parameter that will be used in the sampling.

The third column is the deadVolume of the parameter. This is used to calculate the volume of the parameter that will not be pipetted by the robot (because of viscosity).

The fourth column is the specific ratios we want to have for this parameter. If nothing defined, then take ratios given in program options. If one single number is given, then take this number as a const value.

## Output
The output file is:
<ul>
<li><code>sampling.csv</code>: contains the sampling values</li>
</ul>

# Help
Display help by running:
~~~bash
python -m icfree.sampler --help
~~~

# Authors
Joan Hérisson, Yorgo EL MOUBAYED

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
