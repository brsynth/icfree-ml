#!/bin/sh

# Check if at least one argument is given, and set components_file to the first argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <components_file>"
    exit 1
fi
components_file=$1

# PLATE 0
echo "### PLATE 0 ###"
folder=$PWD
sampling_file=$folder/sampling_volumes.csv
nb_replicates=1
# sampling_file=$folder/sampling_volumes-wo_replicates.csv
# nb_replicates=4
echo "Waiting for $sampling_file... (Ctrl+C to stop)"
read -n 1 -s

python -m icfree \
                --sampler_input_filename $components_file \
          --plate_designer_sampling_file $sampling_file \
          --plate_designer_well_capacity "K-glutamate=50000" \
  --plate_designer_default_well_capacity 60000 \
          --plate_designer_sample_volume 6000 \
    --plate_designer_default_dead_volume 20000 \
         --plate_designer_num_replicates $nb_replicates \
     --plate_designer_start_well_src_plt A1 \
          --plate_designer_output_folder $folder \
            --instructor_output_filename $folder/instructions.csv \
        --instructor_max_transfer_volume 1000 \
            --instructor_split_threshold 1020 \
          --instructor_source_plate_type default:384PP_AQ_GP3,NTP:384PP_AQ_CP,DNA:384PP_AQ_CP,PEG-8000:384PP_AQ_CP


# PLATE 1 re-done
echo "### PLATE 1 (re-done) ###"
folder=Aisha/PLATE1
sampling_file=$folder/plate1_ucb50.csv
# sampling_file=$folder/samples_output-wo_replicates.csv
# nb_replicates=6
echo "Waiting for $sampling_file... Press a key to continue (Ctrl+C to stop)"
read -n 1 -s
python -m icfree \
                --sampler_input_filename $components_file \
          --plate_designer_sampling_file $sampling_file \
          --plate_designer_well_capacity "K-glutamate=50000" \
  --plate_designer_default_well_capacity 60000 \
          --plate_designer_sample_volume 6100 \
    --plate_designer_default_dead_volume 20000 \
         --plate_designer_num_replicates $nb_replicates \
     --plate_designer_start_well_src_plt A1 \
          --plate_designer_output_folder $folder \
            --instructor_output_filename $folder/instructions.csv \
        --instructor_max_transfer_volume 1000 \
            --instructor_split_threshold 1020 \
            --instructor_split_components "HEPES,Amino acid,K-glutamate" \
          --instructor_source_plate_type default:384PP_AQ_GP3,NTP:384PP_AQ_CP,DNA:384PP_AQ_CP,PEG-8000:384PP_AQ_CP


# PLATE 2
echo "### PLATE 2 ###"
folder=Aisha/PLATE2
sampling_file=$folder/sampling_volumes.csv
nb_replicates=1
# nb_replicates=5
echo "Waiting for $sampling_file... Press a key to continue (Ctrl+C to stop)"
read -n 1 -s
python -m icfree \
                --sampler_input_filename $components_file \
          --plate_designer_sampling_file $sampling_file \
          --plate_designer_well_capacity "K-glutamate=50000" \
  --plate_designer_default_well_capacity 60000 \
          --plate_designer_sample_volume 6000 \
    --plate_designer_default_dead_volume 20000 \
         --plate_designer_num_replicates $nb_replicates \
     --plate_designer_start_well_src_plt A10 \
          --plate_designer_output_folder $folder \
            --instructor_output_filename $folder/instructions.csv \
        --instructor_max_transfer_volume 1000 \
            --instructor_split_threshold 1020 \
            --instructor_split_components "HEPES,Amino acid" \
          --instructor_source_plate_type default:384PP_AQ_GP3,NTP:384PP_AQ_CP,DNA:384PP_AQ_CP,PEG-8000:384PP_AQ_CP

    #              --sampler_input_filename $components_file \
    #       --plate_designer_sampling_file $sampling_file \
    #       --plate_designer_well_capacity 55000 \
    #       --plate_designer_sample_volume 6000 \
    # --plate_designer_default_dead_volume 20000 \
    #      --plate_designer_num_replicates $nb_replicates \
    #  --plate_designer_start_well_src_plt A10 \
    #       --plate_designer_output_folder $folder \
    #          --instructor_output_filename $folder/instructions.csv \
    #      --instructor_max_transfer_volume 1000 \
    #          --instructor_split_threshold 1020 \
    #         --instructor_split_components "HEPES,Amino acid,K-glutamate" \
    #        --instructor_source_plate_type default:384PP_AQ_GP3,NTP:384PP_AQ_CP,DNA:384PP_AQ_CP,PEG-8000:384PP_AQ_CP


# PLATE 3
echo "### PLATE 3 ###"
folder=Aisha/PLATE3
sampling_file=$folder/plate3_all_experiments.csv
nb_replicates=5
echo "Waiting for $sampling_file... Press a key to continue (Ctrl+C to stop)"
read -n 1 -s
python -m icfree \
                --sampler_input_filename $components_file \
          --plate_designer_sampling_file $sampling_file \
          --plate_designer_well_capacity "K-glutamate=50000" \
  --plate_designer_default_well_capacity 60000 \
          --plate_designer_sample_volume 6000 \
    --plate_designer_default_dead_volume 20000 \
         --plate_designer_num_replicates $nb_replicates \
     --plate_designer_start_well_src_plt A1 \
          --plate_designer_output_folder $folder \
            --instructor_output_filename $folder/instructions.csv \
        --instructor_max_transfer_volume 1000 \
            --instructor_split_threshold 1020 \
            --instructor_split_components "HEPES,Amino acid" \
          --instructor_source_plate_type default:384PP_AQ_GP3,NTP:384PP_AQ_CP,DNA:384PP_AQ_CP,PEG-8000:384PP_AQ_CP

    #              --sampler_input_filename $components_file \
    #       --plate_designer_sampling_file $sampling_file \
    #       --plate_designer_well_capacity 55000 \
    #       --plate_designer_sample_volume 6000 \
    # --plate_designer_default_dead_volume 20000 \
    #      --plate_designer_num_replicates $nb_replicates \
    #  --plate_designer_start_well_src_plt A1 \
    #       --plate_designer_output_folder $folder \
    #          --instructor_output_filename $folder/instructions.csv \
    #      --instructor_max_transfer_volume 1000 \
    #          --instructor_split_threshold 1020 \
    #         --instructor_split_components "HEPES,Amino acid,K-glutamate" \
    #        --instructor_source_plate_type default:384PP_AQ_GP3,NTP:384PP_AQ_CP,DNA:384PP_AQ_CP,PEG-8000:384PP_AQ_CP

