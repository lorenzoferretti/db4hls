#!/bin/bash

# ==============================================================================
# DSE Configuration
# ==============================================================================

# Name of the top function
TOP_MODULE=$1

# Name fo the design
ARCH=$2

# Vivado HLS timeout
MAX_TIME=$3

# Destination folder of the synthesis
SYN_DIR=$4

# TCL scripts source folder
SCRIPT_DIR=$5

SYNTHESIS_REPORT_ZIP_FOLDER=$6

# Result directory
# RESULT_DIR=$6

# ==============================================================================
# Host constraints
# ==============================================================================

# Max execution time.
TIMEOUT_TIME=MAX_TIME

# Run at most THREADS - 2 instances of Vivado HLS / Vivado.
MAX_THREADS=$(lscpu | grep -E '^CPU\(' | awk '{print $2}')
THREADS=$(("${MAX_THREADS}-2"))

# ==============================================================================
# HLS, Logic Synthesis, Reports
# ==============================================================================

# Enable/disable Vivado HLS, Vivado (logic synthesis), and result collection.
RUN_HLS=1
RUN_LOG=1

# Remove previous intermediate files.
RUN_CLEAN=1

# ==============================================================================
# Files and directories
# ==============================================================================

# GNU Parallel log of jobs.
JOB_LOG=./dse_$TOP_MODULE\_$ARCH.jobs.log

# ==============================================================================
#
# GNU Parallel configuration.
#
# This iteration of the "RF stress script" uses GNU Parallel.
#
# See 'man parallel' for details
#
# This is the first time I found a licensing disclaimer like this:
#
# Academic tradition requires you to cite works you base your article on.
# When using programs that use GNU Parallel to process data for publication
# please cite:
#
#  O. Tange (2011): GNU Parallel - The Command-Line Power Tool,
#    ;login: The USENIX Magazine, February 2011:42-47.
#
#    This helps funding further development; AND IT WON'T COST YOU A CENT.
#    If you pay 10000 EUR you should feel free to use GNU Parallel without citing.
#
# ==============================================================================

# Do not swap.
#SWAP=--noswap

# ==============================================================================
# Functions
# ==============================================================================
#
# Print some general information on the console.
#
print_info ()
{
    candidates=$(get_candidate_uarchs | tr '\n' ' ')
    candidate_count=$(echo $candidates | wc -w)
    cpus=$(lscpu | grep -E '^CPU\(' | awk '{print $2}')
    memory_kb=$(vmstat -s | grep "total memory" | awk '{print $1}')
    memory_mb=$((memory_kb / 1024))
    # TODO: port to floating-point arithmetics
    MAX_TIME_HH=$(((TIMEOUT_TIME / 60) / 60))
    MAX_TIME_MM=$(((TIMEOUT_TIME % 60) / 60))
    MAX_TIME_SS=$(((TIMEOUT_TIME % 60) % 60))
    OVERALL_MAX_TIME=$(((TIMEOUT_TIME * candidate_count) / THREADS))
    OVERALL_MAX_TIME_HH=$(((OVERALL_MAX_TIME / 60) / 60))
    OVERALL_MAX_TIME_MM=$(((OVERALL_MAX_TIME % 60) / 60))
    OVERALL_MAX_TIME_SS=$(((OVERALL_MAX_TIME % 60) % 60))
    echo "INFO: Top Module: $TOP_MODULE"
    echo "INFO: Candidate ARCHs: $candidates"
    echo "INFO: Candidate # $candidate_count"
    echo "INFO: Job # $THREADS on a $cpus-thread CPU"
    echo "INFO: Maximum available memory: $memory_kb KB (= $memory_mb MB)"
    echo "INFO: Single-run timeout*: $TIMEOUT_TIME secs (= $MAX_TIME_HH hours, $MAX_TIME_MM mins, $MAX_TIME_SS secs) * Worst case"
    echo "INFO: Total maximum time*: $OVERALL_MAX_TIME secs (= $OVERALL_MAX_TIME_HH hours, $OVERALL_MAX_TIME_MM mins, $OVERALL_MAX_TIME_SS secs) * Worst case"
    echo -n "INFO: Do you want to proceed? [yes/NO]: "
    read answer
    if [ ! "$answer" == "yes" ]; then
       echo "INFO: Terminated by the user"
       exit 0
    fi
}

#
# Print the candidate architectures on the output console.
#
get_candidate_uarchs ()
{
    #for i in $USER_DEFINED_UARCHS; do echo $i; done
    cat "${SCRIPT_DIR}/${TOP_MODULE}_${ARCH}_batch.txt"
}

#
# Run Vivado HLS and Vivado (logic synthesis).
#
run_parallel4hls_vivado ()
{
    echo "===> $1"
    uarch=$1
    cd $SYN_DIR

    timeout -k 2 $TIMEOUT_TIME vivado_hls -f ../hls_scripts/${uarch}.tcl -l vivado_hls_$uarch.log &> /dev/null
    VIVADO_HLS_STATUS=$?

    PROJECT_DIR=${TOP_MODULE}-${ARCH}-${uarch}
    SOLUTION=solution
    VIVADO_HLS_REPORT_XML="$PROJECT_DIR/$SOLUTION/syn/report/csynth.xml"
    VIVADO_HLS_REPORT_XML_FILES="$PROJECT_DIR/$SOLUTION/syn/report/*.xml"
    VIVADO_HLS_LOG="vivado_hls_$uarch.log"
    VIVADO_REPORT_XML="$PROJECT_DIR/$SOLUTION/impl/report/verilog/myproject_export.xml"
    VIVADO_LOG="$PROJECT_DIR/$SOLUTION/impl/verilog/autoimpl.log"

    #cd ..    
    #echo $SRC_DIR
    cd $SRC_DIR
    #echo "FOLDER SUPPOSED TO CONTAIN PYTHON SCRIPT"
    #pwd
    echo "HERE RESULTS CAN BE COLLECTED AND WRITTEN IN THE DB"
#     python ./collect_results.py $VIVADO_HLS_REPORT_XML $VIVADO_HLS_LOG $VIVADO_HLS_STATUS $VIVADO_REPORT_XML $VIVADO_LOG $VIVADO_STATUS $TIMEOUT_TIME $PROJECT_DIR.tar.bz2 $SYN_DIR $PROJECT_DIR

#Collect results here
#Collect results here
    #echo $SYN_DIR
    cd $SYN_DIR
    #echo "FOLDER SUPPOSED TO CONTAIN SYNTHESIS RESULTS"
    #pwd
    echo $(ls $VIVADO_HLS_REPORT_XML $VIVADO_HLS_LOG $VIVADO_REPORT_XML $VIVADO_LOG 2>/dev/null)
    tar cfj $PROJECT_DIR.tar.bz2 $(ls $VIVADO_HLS_REPORT_XML_FILES $VIVADO_HLS_LOG $VIVADO_REPORT_XML $VIVADO_LOG 2>/dev/null) &> /dev/null
    mv $PROJECT_DIR.tar.bz2 $SYNTHESIS_REPORT_ZIP_FOLDER/$PROJECT_DIR.tar.bz2
#Remove files generated for the synthesis    
    rm -rf $PROJECT_DIR
    rm -f $VIVADO_HLS_LOG
    rm -f ../hls_scripts/${uarch}.tcl
    rm -f ../hls_scripts/${uarch}.dir
}


# ==============================================================================
# The top of the hill :-)
# ==============================================================================

# These exports are necessary for GNU Parallel.
export -f run_parallel4hls_vivado
export TOP_MODULE
export SYN_DIR
export ARCH
export RUN_CLEAN
export RUN_HLS
export TIMEOUT_TIME
export SRC_DIR
export SYN_DIR
export SCRIPT_DIR
export SYNTHESIS_REPORT_ZIP_FOLDER

# Print some info, run the stress tests with GNU parallel, and eventually collect the results.
print_info
get_candidate_uarchs | parallel --progress --will-cite --jobs $THREADS $SWAP --joblog $JOB_LOG run_parallel4hls_vivado
#get_candidate_uarchs | parallel --progress --will-cite --timeout $TIMEOUT_TIME --jobs $THREADS $SWAP --joblog $JOB_LOG run_hls4ml_vivado
#collect_results
