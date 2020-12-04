''' Author: Lorenzo Ferretti
    Contact: lorenzo.ferretti@usi.ch 

This python script shows how to process a configuration space descriptor (CSD) file.
The stucture generated is then used to automatically create the VivadoHLS scritps
and run an exaustive exploration over the defined configuration space.

NOTE: Before run this script please exhecute sh ./db4hls_confing.sh
'''

import synthesis

### Set all project and environmental variables

# Specify the tool and the fpga model (currently only vivado_hls is supported)
synthesis_tool = "vivado_hls"
technology = "xczu9eg-ffvb1156-2-e"

# Specify the path of the source files
src_files_path = ""

# List of the source file names
src_files = ["",""]

# Testbench file if cosimulation is requried
testbench = ""

# Specify top_module (name of the function to be synthesised)
synth = synthesis.Synthesiser(synthesis_tool)

# Specify destination folder of the synthesis
destination_folder_path = ""

# Specify destination folder of the hls file generated
hls_scripts_folder_path = "../"

# Specify the configuration space descriptor file
csd_file = "../csd_files/last_step_scan_radix_sort.sweep"


### Start processing

# Create synthesiser
synth = synthesis.Synthesiser(synthesis_tool)

# Set synthesised project data and board spec
synth.set_project(src_files_path, src_files, testbench, top_module, implementation,
                  destination_folder_path, hls_scripts_folder_path)
synth.set_board_specs(technology)

# Process the configuration space descriptor
csd = synth.set_exploration_knobs(csd_file)
new_feature_sets = ds['Knobs_values']
