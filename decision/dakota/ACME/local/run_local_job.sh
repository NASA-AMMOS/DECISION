#######################################
# Create relevant paths to help with the job management
# NOTE: You may need/want to update the below paths

# Trying to contain everything inside /decision itself
# 
# Directory to save output results to. Likely want this in a different spot than
# DECISION code to avoid adding cruft to the git-tracked repo
# export SCRATCH=/Volumes/MLIA_active_data/data_DECISION/dakota_runs/local
# # Path to OWLS source code
# export OWLS_SRC_DIR=~/Builds/OWLS-Autonomy/src
# # Path to DECISION source code
# export DECISION_DIR=~/Builds/DECISION/decision

# DECISION source code
export DECISION_DIR=${PWD}

# OWLS source code
export OWLS_DIR=${DECISION_DIR}/OSIA/OWLS-Autonomy/src

# Path to dakota.in file
#export DAKOTA_IN_DIR=${DECISION_DIR}/dakota/local

# Set env vars below for use within acme_docker_trigger.sh
export DATA_DIR=${DECISION_DIR}/data/ACME_Demo_Data

# Datetime for current run
export DATETIME=$1

# Match number of processes (np) to number of nodes
dakota -i ${DECISION_DIR}/dakota/ACME/local/dakota.in > ${DECISION_DIR}/runs/${DATETIME}/dakota.out
