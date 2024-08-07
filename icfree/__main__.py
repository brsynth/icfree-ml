import argparse
import os
import sys

# Import main functions from the modules
from icfree.sampler import main as sampler_main
from icfree.plate_designer import main as plate_designer_main
from icfree.instructor import main as instructor_main

def generate_snakefile(args):
    output_folder = args.plate_designer_output_folder
    os.makedirs(output_folder, exist_ok=True)

    snakefile_content = f"""
rule all:
    input:
        "{args.instructor_output_filename}"

rule SAMPLER:
    input:
        components="{args.sampler_input_filename}"
    output:
        csv="{args.plate_designer_sampling_file}"
    params:
        nb_samples={args.sampler_nb_samples},
        seed={args.sampler_seed},
        step={args.sampler_step}
    shell:
        "python -m icfree.sampler {{input.components}} {{output.csv}} {{params.nb_samples}} --step {{params.step}} --seed {{params.seed}}"

rule PLATE_DESIGNER:
    input:
        sampling_file=rules.SAMPLER.output.csv
    output:
        source_plate="{output_folder}/source_plate.csv",
        destination_plate="{output_folder}/destination_plate.csv"
    params:
        sample_volume={args.plate_designer_sample_volume},
        default_dead_volume={args.plate_designer_default_dead_volume},
        dead_volumes="{args.plate_designer_dead_volumes}",
        num_replicates={args.plate_designer_num_replicates},
        default_well_capacity={args.plate_designer_default_well_capacity},
        well_capacity="{args.plate_designer_well_capacity}",
        start_well_src_plt="{args.plate_designer_start_well_src_plt}",
        start_well_dst_plt="{args.plate_designer_start_well_dst_plt}",
        output_folder="{args.plate_designer_output_folder}"
    shell:
        '''
        python -m icfree.plate_designer {{input.sampling_file}} {{params.sample_volume}} \\
        --default_dead_volume {{params.default_dead_volume}} \\
        --dead_volumes {{params.dead_volumes}} \\
        --num_replicates {{params.num_replicates}} \\
        --default_well_capacity {{params.default_well_capacity}} \\
        --well_capacity {{params.well_capacity}} \\
        --start_well_src_plt {{params.start_well_src_plt}} \\
        --start_well_dst_plt {{params.start_well_dst_plt}} \\
        --output_folder {{params.output_folder}}
        '''

rule INSTRUCTOR:
    input:
        source_plate=rules.PLATE_DESIGNER.output.source_plate,
        destination_plate=rules.PLATE_DESIGNER.output.destination_plate
    output:
        instructions="{args.instructor_output_filename}"
    params:
        max_transfer_volume={args.instructor_max_transfer_volume},
        split_threshold={args.instructor_split_threshold},
        source_plate_type="{args.instructor_source_plate_type}",
        split_components="{args.instructor_split_components}"
    shell:
        "python -m icfree.instructor {{input.source_plate}} {{input.destination_plate}} {{output.instructions}} --max_transfer_volume {{params.max_transfer_volume}} --split_threshold {{params.split_threshold}} --source_plate_type '{{params.source_plate_type}}' --split_components '{{params.split_components}}'"
    """
    with open('Snakefile', 'w') as file:
        file.write(snakefile_content)

def run_snakemake(args):
    # Simulating Snakemake workflow by directly calling the main functions

    # SAMPLER
    sampler_main(args.sampler_input_filename, args.plate_designer_sampling_file, args.sampler_nb_samples, args.sampler_step, args.sampler_seed)
    
    # PLATE_DESIGNER
    plate_designer_main(
        args.plate_designer_sampling_file,
        args.plate_designer_sample_volume,
        args.plate_designer_start_well_src_plt,
        args.plate_designer_start_well_dst_plt,
        "16x24",  # Assuming default plate dimensions
        args.plate_designer_well_capacity,
        args.plate_designer_default_well_capacity,
        args.plate_designer_dead_volumes,
        args.plate_designer_default_dead_volume,
        args.plate_designer_num_replicates,
        args.plate_designer_output_folder
    )
    
    # INSTRUCTOR
    instructor_main(
        f"{args.plate_designer_output_folder}/source_plate.csv",
        f"{args.plate_designer_output_folder}/destination_plate.csv",
        args.instructor_output_filename,
        args.instructor_source_plate_type,
        args.instructor_max_transfer_volume,
        args.instructor_split_threshold,
        args.instructor_split_components
    )

def main():
    parser = argparse.ArgumentParser(description="Generate and run a Snakemake workflow based on user parameters.")
    parser.add_argument('--sampler_input_filename', required=True, help="Input filename for the SAMPLER step.")
    parser.add_argument('--sampler_nb_samples', default=100, type=int, help="Number of samples (default: 100).")
    parser.add_argument('--sampler_seed', default=42, type=int, help="Seed for sampling (default: 42).")
    parser.add_argument('--sampler_step', default=10, type=float, help="Step size for sampling (default: 10).")
    parser.add_argument('--plate_designer_sample_volume', default=2000, type=int, help="Sample volume for plate designer (default: 2000).")
    parser.add_argument('--plate_designer_default_dead_volume', default=20000, type=int, help="Default dead volume (default: 20000).")
    parser.add_argument('--plate_designer_dead_volumes', default="RNA=15000,Water=15000", help="Dead volumes for specific components (default: 'RNA=15000,Water=15000').")
    parser.add_argument('--plate_designer_num_replicates', default=3, type=int, help="Number of replicates for plate design (default: 3).")
    parser.add_argument('--plate_designer_default_well_capacity', default=60000, type=int, help="Default well capacity for plate designer (default: 60000).")
    parser.add_argument('--plate_designer_well_capacity', default="RNA=50000,Water=60000", help="Well capacity for specific components (default: 'RNA=50000,Water=60000').")
    parser.add_argument('--plate_designer_start_well_src_plt', default="A1", help="Start well for source plate (default: 'A1').")
    parser.add_argument('--plate_designer_start_well_dst_plt', default="A1", help="Start well for destination plate (default: 'A1').")
    parser.add_argument('--plate_designer_output_folder', default="output", help="Output folder for plate designer (default: 'output').")
    parser.add_argument('--plate_designer_sampling_file', required=True, help="Output file for samples generated by the SAMPLER step.")
    parser.add_argument('--instructor_output_filename', required=True, help="Output filename for the INSTRUCTOR step.")
    parser.add_argument('--instructor_max_transfer_volume', default=500, type=int, help="Maximum transfer volume (default: 500).")
    parser.add_argument('--instructor_split_threshold', default=580, type=int, help="Split threshold (default: 580).")
    parser.add_argument('--instructor_source_plate_type', default="default:384PP_AQ_GP3", help="Source plate type for the INSTRUCTOR (default: 'default:384PP_AQ_GP3').")
    parser.add_argument('--instructor_split_components', default="", help="Split components for the INSTRUCTOR (default: '').")
    
    args = parser.parse_args()
    
    generate_snakefile(args)
    
    # Run Snakemake simulation by calling main functions directly
    run_snakemake(args)

if __name__ == "__main__":
    main()
