#!/bin/bash

# Initialize Conda for this shell session
source ~/miniconda3/etc/profile.d/conda.sh

# Activate the Conda environment named 'decision'
conda activate decision

# Run the dakota executable with all the passed arguments
exec dakota "$@"
