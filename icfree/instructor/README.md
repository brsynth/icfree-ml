
# Instructor
The module generates a list of instructions to perform the experiment.

## Running from the CLI
~~~bash
python -m icfree.instructor 
  --source_plates <source_plate file 1> <source_plate file 2>... \
  --dest_plates <dest_plate file 1> <dest_plate file 2>... \
~~~

## Options
<ul>
  <li><code>-of</code>, <code>--output-folder</code>: Output folder to write output files (default: working dir)</li>
  <li><code>--robot</code>: Robot name (default: echo)</li>
  <li><code>--source_plates</code>: Source plates files.</li>
  <li><code>--dest_plates</code>: Destination plates files.</li>
</ul>

## Example
~~~bash
python -m icfree.instructor \
  --source_plates out/source_plate_1.json \
  --dest_plates out/destination_plate_1.json \
  --robot echo \
  -of out
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
python -m icfree.instructor --help
~~~

# Authors
Joan Hérisson, Yorgo EL MOUBAYED

# License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
