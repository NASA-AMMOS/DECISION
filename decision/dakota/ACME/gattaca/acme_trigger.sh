module load singularity-gattaca/compute

#######################################
# Insert dakota inputs into ACME config template
echo "ACME Trigger: Preparing dakota inputs with dprepro; params input at: ${1}"
dprepro $1 acme_config.template acme_config.yml

# Create env vars that will be passed to singularity.
# SINGULARIY_BIND is a special env var that will mount those directories to the singularity container
export DATA_DIR="/scratch_lg/decision-hpc/data/ACME/Hand_Labels_2021"
export SINGULARITY_BIND="${DATA_DIR},${PWD}"
export ACME_PREDS_DIR=./ACME_preds
export ACME_EVAL_DIR=./ACME_eval_logs_master
mkdir $ACME_PREDS_DIR
mkdir $ACME_EVAL_DIR

#######################################
# ACME Processing and Eval
echo "ACME Trigger: Executing singularity container..."

singularity exec --workdir /app \
/scratch_lg/decision-hpc/containers/owls-autonomy-acme-v1.sif \
/app/ACME_processing_and_eval.sh \
"${DATA_DIR}/pickles/combined/*.pickle" \
"${ACME_PREDS_DIR}" \
"${PWD}/acme_config.yml" \
"${ACME_PREDS_DIR}/*/*_peaks.csv" \
"${DATA_DIR}/labels/combined/*.csv" \
"${ACME_EVAL_DIR}"

#######################################
# Once processing is done, execute python script to convert the container's output into something dakota can ingest
echo "ACME Trigger: Exporting dakota results. Input at: ${1}; output at ${2}"
python dakota_output_writer.py --dakota_input $1 --dakota_output $2 --acme_output_dir "${ACME_EVAL_DIR}"

# Also remove mugshots here to limit disk usage
rm -r $ACME_PREDS_DIR/*/Mugshots