''' Author: Lorenzo Ferretti
    Contact: lorenzo.ferretti@usi.ch 

This python script shows how to process a configuration space descriptor (CSD) file.
The stucture generated is then used to automatically create the VivadoHLS scritps
and run an exaustive exploration over the defined configuration space.

NOTE: Before run this script please exhecute sh ./db4hls_confing.sh
'''

import synthesis
import VivadoHLS

### Set all project and environmental variables

# Specify the tool and the fpga model (currently only vivado_hls is supported)
synthesis_tool = "vivado_hls"
technology = "xczu9eg-ffvb1156-2-e"

# Specify the path of the source files
# Assuming that the Machsuite benchmark folder is in the project root level
# src_files_path = "../MachSuite/backprop/backprop/"
src_files_path = "../../DSE_exhaustive/benchmark/MachSuite/backprop/backprop/"

# List of the source file names
src_files = ["backprop.c","backprop.h"]

# Testbench file if cosimulation is requried
testbench = ""

# Specify the design
design = "backprop"

# Specify top_module (name of the function to be synthesised)
top_module = "get_delta_matrix_weights1"

# Specify destination folder of the synthesis while executed
destination_folder_path = "../syn/"

# Specify destination folder of the hls file generated
hls_scripts_folder_path = "../tcl_scripts/"

# Specify destination folder that will contained the compressed outcome of the syntehsis
synthesis_zip_folder = "../syn_zip/"

# Specify the configuration space descriptor file
csd_file = "../csd_files/get_delta_matrix_weights1_test.sweep"

# Specify the maximum amount of time allowed per synthesis in seconds (1h = 3600s)
max_synthesis_time = 3600

# Specify the maximum number of cores to use duiring the exploration. (Leave at least one or two cores available)
number_of_cores = 6

### Start processing

# Create synthesiser
synth = synthesis.Synthesiser(synthesis_tool)

# Set synthesised project data and board spec
synth.set_project(src_files_path, src_files, testbench, top_module, design,
                  destination_folder_path, hls_scripts_folder_path, synthesis_zip_folder)
synth.set_board_specs(technology)

# Process the configuration space descriptor
configuration_space_descriptor = synth.set_exploration_knobs(csd_file)
knob_value_sets = configuration_space_descriptor['Knobs_values']

print(knob_value_sets)

# Generate configurations from configuration space descriptor
configs = synth.exhaustive_configs()
for c in configs:
    print(c)

synth.synthesise_batch(configs, configuration_space_descriptor, number_of_cores, max_synthesis_time)

