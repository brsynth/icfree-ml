
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

# Concentrations Sampler
This module generates a list of concentrations for all parameters given in the input file. The concentrations are generated using a Latin Hypercube Sampling (LHS) method. The number of concentrations generated is given by the user and the concentrations are saved in (a) csv file(s).

The LHS values are generated using the `lhs` function from the `pyDOE` package and binned into bins to reduce the combinatorial space.

## Running from the CLI

~~~bash
python -m icfree.plates_generator <cfps-parameters tsv file> -of <output_folder>
~~~

## Options
<ul>
<li><code>-of</code> or <code>--output_folder</code>: path to the output folder where the generated plates will be saved</li>
<li><code>--nb-sampling-steps</code>: Number of values for all factors when performing the sampling (default: 5)</li>
<li><code>--sampling-ratios</code>: Ratios for all factors when performing the sampling</li>
<li><code>--nb-samples</code>: Number of samples to generate for all factors when performing the sampling (default: 99)</li>
<li><code>--seed</code>: Seed to reproduce results (same seed number = same results)</li>
<li><code>--all-status</code>: Change status of all parameters (but DNA) (choices: <code>doe</code> or <code>const</code>)</li>
</ul>

## Input file

Below is an example of an input file:
| **Parameter** 	| **Status** 	| **Maximum value** 	| **Stock concentration** 	| **Parameter dead volume** 	| **Ratios** 	|
|---------------	|------------	|---------------------------	|-------------------------	|---------------------------	|--------------------------	|
| Mg-glutamate  	| doe        	| 4                         	| 168                     	| 0                         	| 0.0,0.1,0.3,0.5,1.0      	|
| k-glutamate   	| doe        	| 80                        	| 3360                    	| 0                         	|                          	|
| CoA           	| doe        	| 0.26                      	| 210                     	| 0                         	|                          	|
| 3-PGA         	| doe        	| 30                        	| 1400                    	| 0                         	|                          	|
| NTP           	| doe        	| 1.5                       	| 630                     	| 0                         	|                          	|
| NAD           	| doe        	| 0.33                      	| 138.6                   	| 0                         	|                          	|
| Folinic acid  	| doe        	| 0.068                     	| 28.56                   	| 0                         	|                          	|
| Spermidine    	| doe        	| 1                         	| 420                     	| 0                         	|                          	|
| tRNA          	| doe        	| 0.2                       	| 84                      	| 0                         	|                          	|
| Amino acids   	| doe        	| 1.5                       	| 6                       	| 0                         	|                          	|
| CAMP          	| doe        	| 0.75                      	| 200                     	| 0                         	|                          	|
| Extract       	| const      	| 30                        	| 300                     	| 2000                      	|                          	|
| HEPES         	| const      	| 50                        	| 2100                    	| 0                         	|                          	|
| PEG           	| const      	| 2                         	| 200                     	| 4000                      	|                          	|
| Promoter      	| const      	| 10                        	| 300                     	| 0                         	|                          	|
| RBS           	| const      	| 10                        	| 200                     	| 0                         	|                          	|
| GFP-DNA       	| dna_fluo   	| 50                        	| 300                     	| 0                         	|                          	|
| GOI-DNA       	| dna_goi    	| 50                        	| 300                     	| 0                         	|                          	|

The first column is the parameter (or factor) names.

The second column indicates how parameters will be combined:
<ol>
    <li><code>doe</code>: parameter values will be combined in a Design of Experiment algorithm (currently Latin Hypercube Sampling).</li>
    <li><code>const</code>: parameter values will be kept constant.</li>
    <li><code>dna_*</code>: parameter values will combined in almost full combinatorial: all possible combinations of values will be generated, except for the case where there is only the GOI (Gene Of Interest):

|  	| DNA (reporter) 	| DNA (GOI) 	|
|---	|---	|---	|
| autofluorescence 	| 0 	| 0 	|
| normalizer 	| 1 	| 1 	|
| initial 	| 1 	| 0 	|
</li>
</ol>

The third column is the maximum value of the parameter that will be used in the DoE algorithm.

The fourth column is the stock concentration of the parameter. This is used to calculate the volume of the parameter to add to the plate.

The fifth column is the dead volume of the parameter. This is used to calculate the volume of the parameter that will not be pipetted by the robot (because of viscosity).

The sixth column is the specific ratios we want to have for this parameter. If nothing defined, then take ratios given in program options.

## Output files
If <code>dna_*</code> parameters are present in the input file, then the output files will be:
<ul>
<li><code>initial.csv</code>: contains the concentrations of all non-dna parameters and maximum concentration for the reporter and 0 for the GOI</li>
<li><code>normalizer.csv</code>: contains the concentrations of all non-dna parameters and maximum concentration for the reporter and GOI</li>
<li><code>autofluorescence.csv</code>: contains the concentrations of all non-dna parameters and 0 for the reporter and GOI</li>
</ul>

If <code>dna_*</code> parameters are not present in the input file, then the output file will be:
<ul>
<li><code>concentrations.csv</code>: contains the concentrations of all parameters</li>
</ul>


# ECHO Instructor
## Running from the CLI

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
