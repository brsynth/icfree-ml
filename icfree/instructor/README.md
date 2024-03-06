
# Instructor
The module generates a list of instructions to perform the experiment on a given liquid handler (e.g. ECHO).

<!-- resize and center image -->
<p align="center">
<img src="/img/instructor.png" width="500">
</p>

### Running from the CLI
~~~bash
python -m icfree.instructor 
  --source_plates <src_plate_file_1.csv> <src_plate_file_2.csv>... \
  --dest_plates <dst_plate_file_1.csv> <dst_plate_file_2.csv>... \
~~~

### Positional arguments
* <code>--source-plates</code>: Source plates files.</li>
* <code>--destination-plates</code>: Destination plates files.</li>
* <code>-of</code>, <code>--output-file</code>: Output file to write output files (default: working dir)

### Optional arguments
<ul>
  <li><code>-suv</code>, <code>--split-upper-vol</code>: Max value for volume transfer, split instruction beyond this value.</li>
  <li><code>-slv</code>, <code>--split-lower-vol</code>: If the last split instruction transfers a volume below this value, re-integrate this volume to the penultimate split instruction.</li>
  <li><code>-soc</code>, <code>--split-outfile-components</code>: Generate one output file per component specified in this list.</li>
  <li><code>-spt</code>, <code>--src-plate-type</code>: Specifies the plate type for each component listed (default: 'ALL:384PP_AQ_GP3').</li>
</ul>

### Example
~~~bash
python -m icfree.instructor \
  --source_plates tests/data/instructor/input/source_plate.csv \
  --dest_plates tests/data/instructor/input/destination_plate.csv \
  --robot echo \
  -of out
~~~

with:
* [source_plate.csv](/tests/data/instructor/input/source_plate.csv): File containing the source plate description.
* [destination_plate.csv](/tests/data/instructor/input/destination_plate.csv): File containing the destination plate description.

### Output
The output files is:

* [instructions.csv](/tests/data/instructor/output/instructions.csv): contains the instructions to perform the experiment on the ECHO machine

### Help
Display help by running:
~~~bash
python -m icfree.instructor --help
~~~

### Authors
Joan Hérisson (with help of ChatGPT-4)

### License
Released under the MIT licence. See the [LICENSE](https://github.com/brsynth/icfree-ml/blob/main/LICENSE.md) file for details.
