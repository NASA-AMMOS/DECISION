#!/bin/bash -l
#PBS -q mpi-jpl
#PBS -l select=100:ncpus=4:mem=6gb
#PBS -l walltime=72:00:00
#PBS -j oe
# To add email alerts, add "#PBS -m abe"
# Specify the email address like "#PBS -M wronk@jpl.nasa.gov"
#PBS -N decision_dakota_test
#PBS -W group_list=decision-hpc
#PBS -o /scratch_lg/decision-hpc/dakota_runs/qsub.out
#PBS -e /scratch_lg/decision-hpc/dakota_runs/qsub.err

#######################################
# Setup Gattaca environment
module load singularity
module load singularity-gattaca/compute
module load dakota

#######################################
# Create relevant paths to help with the job management

# Output directory for trials
export SCRATCH=/scratch_lg/decision-hpc
# Directory of Decision source code
export DECISION_DIR=/scratch_lg/decision-hpc/DECISION/decision
# Directory of dakota.in file
export DAKOTA_IN_DIR=${DECISION_DIR}/dakota/gattaca
# Directory of OWLS source code
export OWLS_SRC_DIR=/home/wronk/Builds/OWLS-Autonomy/src
# Singularity container information
export CONTAINER_ID=owls-autonomy-acme
export CONTAINER_VERSION=v1

echo "Executing run_pbs_job.sh using SCRATCH="${SCRATCH}
# Log commands and results from this point onward in qsub output file
set -v

#######################################
# STAGE JOB

# Set up some env vars around this dakota run
export STUDY_NAME_PREFIX=acme_opt
export RUN_DATE=`date +%Y%m%d%H%M%S`
export STUDY_NAME=${STUDY_NAME_PREFIX}_${RUN_DATE}

# Set up some env vars to relevant paths
export RUN_DIR=${SCRATCH}/dakota_runs/${STUDY_NAME}
export TMPDIR=${RUN_DIR}/tmp  # TODO: Fix this. Using system tmp dir was leading to file write errors 
export OMPI_TMPDIR=${RUN_DIR}/tmp

# For each singularity container (aka a dakota trial), need to copy over code and relevant execution files
mkdir -p   $RUN_DIR
rsync -avz $DECISION_DIR/dakota/ $RUN_DIR/dakota
# Copy in the test directory, which will replace a few files
rsync -avz $DECISION_DIR/dakota/ $RUN_DIR/dakota
rsync -avz $DECISION_DIR/OSIA/ $RUN_DIR/OSIA
mkdir $TMPDIR

# Create a link to the OWLS directory (so we don't have to continually copy over the src code)
ln -s ${OWLS_SRC_DIR} ${RUN_DIR}/OSIA/OWLS-Autonomy/src

# TODO: in future, pull the container directly before each run
#cd $RUN_DIR
#singularity pull ${RUN_DIR}/${CONTAINER_ID}-${CONTAINER_VERSION}.sif docker://registry.jpl.nasa.gov/mlia/${CONTAINER_ID}:$CONTAINER_VERSION

#######################################
# Run dakota job relying on MPI for multiproc
conda activate decision
cd $RUN_DIR

# Match number of processes (np) to number of nodes
mpirun -np 100 dakota -i ${DAKOTA_IN_DIR}/dakota.in > dakota.out
