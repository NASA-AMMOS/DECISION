OA=$(pwd)/OSIA/OWLS-Autonomy
DATA=$(pwd)/data/ACME_Demo_Data
docker run -it --rm \
--volume $DATA:$DATA \
--volume $OA:$OA \
ghcr.io/buggtb/decision:v1 \
$DATA"/tmp/*.pickle" \
$DATA"/ACME_preds/" \
$OA"/src/cli/configs/dakota_acme_config.yml" \
$DATA"/ACME_preds/*/*_peaks.csv" \
$DATA"/labels/*.csv" \
$DATA"/ACME_eval_logs_master/"
