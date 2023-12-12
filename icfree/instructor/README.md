
# Instructor
The module generates a list of instructions to perform the experiment on a given liquid handler (e.g. ECHO).

<!-- resize and center image -->
<p align="center">
<img src="/img/instructor.png" width="500">
</p>

### Running from the CLI
~~~bash
python -m icfree.instructor 
  --source_plates <src_plate_file_1.json> <src_plate_file_2.json>... \
  --dest_plates <dst_plate_file_1.json> <dst_plate_file_2.json>... \
~~~

### Positional arguments
* [src_plate.json](/tests/data/instructor/input/source_plate.json): File containing the source plate description.
* [dst_plate.json](/tests/data/instructor/input/destination_plate.json): File containing the destination plate description.

### Optional arguments
<ul>
  <li><code>-of</code>, <code>--output-folder</code>: Output folder to write output files (default: working dir)</li>
  <li><code>--robot</code>: Robot name (default: echo)</li>
  <li><code>--source_plates</code>: Source plates files.</li>
  <li><code>--dest_plates</code>: Destination plates files.</li>
</ul>

### Example
~~~bash
python -m icfree.instructor \
  --source_plates tests/data/instructor/input/source_plate.json \
  --dest_plates tests/data/instructor/input/destination_plate.json \
  --robot echo \
  -of out
~~~

### Output
The output files is:

* [instructions.csv](/tests/data/instructor/output/instructions.csv): contains the instructions to perform the experiment on the ECHO machine

### Help
Display help by running:
~~~bash
python -m icfree.instructor --help
~~~

### Authors
Joan Hérisson

### License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
