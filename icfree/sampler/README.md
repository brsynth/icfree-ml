
# Sampler
This module generates a list of values for all parameters given in the input file. The values are generated using a Latin Hypercube Sampling (LHS) method (`lhs` function from the `pyDOE` package).

. The number of values generated is given by the user and the values are saved in csv or tsv file.

It is important to note that the user can pass some values that he whishes to combine. In this case, we are dealing with discrete space, and because LHS is working on continuous space the result sampling can contain duplicates. To avoid this, we have set some filters to select the appropriate sampling method. Let consider $N$ the number of possible combinations and $n$ the number of samples to generate. The following rules are applied:
<ul>
<li>If $n <= 1 \over 3 * N$, then LHS is applied. If the result sampling contain duplicates, then we replace them by random samples.</li>
<li>If $n > 1 \over 3 * N$, then LHS is not required and we proceed to random sampling.</li>
<li>If $n == N$, then we generate all the combinations.</li>
</ul>

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
  tests/data/sampler/input/parameters.tsv \
  --nb-samples 100
~~~

## Input file

Below is an example of a [parameters.tsv](/tests/data/sampler/input/parameters.tsv) file:


|Component|maxValue|Ratios|
|---------|--------|------|
|Component_1|125|0.0 0.1 0.3 0.5 1.0|
|Component_2|125|1|
|Component_3|125| |
|Component_4|125| |
|Component_5|125| |
|Component_6|125| |
|Component_7|125| |

The first column is the parameter (or factor) names.

The second column is the maxValue of the parameter that will be used in the sampling.

The third column is the specific ratios we want to have for this parameter:
* if nothing defined, then take ratios given in program options.
* if one single number is given, then take this number as a constant value (no sampling).
* if no value is given, then take the default ratios (`nb_samples` linear ratios from 0 to 1).


## Output
The result obtained from the input file above is: [sampling.csv](/tests/data/converter/output/sampling.tsv)


# Help
Display help by running:
~~~bash
python -m icfree.sampler --help
~~~

# Authors
Joan Hérisson, Yorgo EL MOUBAYED

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
