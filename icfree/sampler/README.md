
# Sampler
This module generates a list of values for all parameters given in the input file. The values are generated using a Latin Hypercube Sampling (LHS) method (`lhs` function from the `scipy.stats.qmc` package).

The number of values generated is given by the user and the values are saved in csv file.

It is important to note that the user can pass some values that he whishes to combine. In this case, we are dealing with discrete space, and because LHS is working on continuous space the result sampling can contain duplicates. To avoid this, we have set some filters to select the appropriate sampling method. Let consider $N$ the number of possible combinations and $n$ the number of samples to generate. The following rules are applied:
<ul>
<li>If $n < \frac{N}{3}$ or if the CLI option <code>--method</code> is set to <code>`lhs`</code>, then LHS is applied. If the result sampling contain duplicates, then we replace them by random samples.</li>
<li>If $n > \frac{N}{3}$ or if the CLI option <code>`--method`</code> is set to <code>`random`</code>, then LHS is not required and we proceed to random sampling.</li>
<li>If $n = N$ or if the CLI option <code>`--method`</code> is set to <code>`all`</code>, then we generate all the combinations.</li>
</ul>

## Running from the CLI
~~~bash
python -m icfree.sampler <input_file.tsv>
~~~

## Options
<ul>  
<li><code>--output-file</code>: path to the output file where the generated sampling will be saved (default: print on stdout)</li>
<li><code>--nb-samples</code>: Number of samples to generate for all factors when performing the sampling (default: 100)</li>
<li><code>--method {lhs, random, all, auto}</code>: sampling method (default: 'auto')</li>
<li><code>--nb-bins</code>: number of values for all factors when performing the sampling</li>
<li><code>--ratios</code>: ratios for creating discrete ranges, e.g. if <code>maxValue</code> is 100 and ratios is set to <code>0 0.1 0.3 0.5 1</code>, available values will be <code>0 10 30 50 100</code>; must be a list of floats between 0.0 and 1.0 (separated by blanks)</li>
<li><code>--seed</code>: seed to reproduce results (same seed number = same results)</li>
</ul>

## Example
~~~bash
python -m icfree.sampler \
  tests/data/sampler/input/parameters.tsv \
  --nb-samples 40 --seed 42
~~~

## Input file

Below is an example of a [parameters.tsv](/tests/data/sampler/input/parameters.tsv) file:


|Component  |maxValue|Ratios&#124;Step&#124;NbBins   |
|-----------|--------|---------------------|
|Component_1|200     |0.0,0.1,0.3,0.5,1.0&#124;&#124;|
|Component_2|125     |1&#124;&#124;                  |
|Component_3|40      |                     |
|Component_4|100     |&#124;10&#124;                 |
|Component_5|400     |&#124;&#124;10                 |
|Component_6|100     |1                    |

The first column is the parameter (or factor) names.

The second column is the maxValue of the parameter that will be used in the sampling.

The third column is the specific ratios, step or number of bins we want to have for this parameter:
* if the first value is set (e.g. `0.1 0.5 1||`), then read it as ratios,
* if the second value is set (e.g. `|10|`), then read it as step, i.e. start from 0 to maxValue with a step of 10,
* if the third value is set (e.g. `||10`), then read it as number of bins, i.e. divide the range from 0 to maxValue into 10 bins,
* if one single number is given, then read this number for ratios (constant value as well, e.g. 0.5),
* if no value is given, then ratios = 1 is considered (constant value).


## Output
The result obtained from the input file above is: [sampling.csv](/tests/data/sampler/output/sampling.csv)


# Help
Display help by running:
~~~bash
python -m icfree.sampler --help
~~~

# Authors
Joan Hérisson (with help of ChatGPT-4)

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
