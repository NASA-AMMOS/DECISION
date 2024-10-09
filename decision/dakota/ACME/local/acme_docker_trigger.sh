#######################################
# Insert dakota inputs into ACME config template
echo "ACME Trigger: Preparing dakota inputs with dprepro; params input at: ${1}"
dprepro $1 acme_config.template acme_config.yml

# copy dakota.in to runs
cp $1 ${DECISION_DIR}/runs/${DATETIME}/

echo $1

#######################################
# ACME Processing and Eval

export ACME_PREDS_DIR=${PWD}/ACME_preds
export ACME_EVAL_DIR=${PWD}/ACME_eval_logs_master
mkdir $ACME_PREDS_DIR
mkdir $ACME_EVAL_DIR

echo "ACME Trigger: Executing Docker container..."
echo "debug"
docker run -it --rm \
--volume $DATA_DIR:$DATA_DIR \
--volume $PWD:$PWD \
owls-autonomy-acme:v1 \
"${DATA_DIR}/tmp/*.pickle" \
"${ACME_PREDS_DIR}" \
"${PWD}/acme_config.yml" \
"${ACME_PREDS_DIR}/*/*_peaks.csv" \
"${DATA_DIR}/labels/*.csv" \
"${ACME_EVAL_DIR}"

#######################################
# Exporting ACME results into dakota format
echo "ACME Trigger: Exporting dakota results. Input at: ${1}; output at ${2}"
python acme_output_writer.py --dakota_input $1 --dakota_output $2 --acme_output_dir "${ACME_EVAL_DIR}"

# Also remove mugshots here to limit disk usage
rm -r $ACME_PREDS_DIR/*/Mugshots
