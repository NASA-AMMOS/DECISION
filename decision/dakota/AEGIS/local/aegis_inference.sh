# DECISION source code
export DECISION_DIR=${PWD}

# AEGIS source code
export AEGIS_DIR=${DECISION_DIR}/OSIA/aegis_rockster_server/aegis_rockster_server

# Set env vars below for use within acme_docker_trigger.sh
export CONTAINER_ID=aegis_rockster_server

export PORT=7625

echo "Looking for a container on port: ${PORT}"
ID=$(\
docker container ls --format="{{.ID}}\t{{.Ports}}" |\
grep ${PORT} |\
awk '{print $1}')
echo "Found Container ID: ${ID}"
#echo "Stopping and removing it"

echo "Starting Server"

docker run --platform linux/arm64/v8 -itd --rm -p ${PORT}:${PORT} ${CONTAINER_ID}

sleep 5

echo "Running AEGIS inference"

export AEGIS_OUTPUT_DIR=${DECISION_DIR}/aegis_inference
mkdir $AEGIS_OUTPUT_DIR

python ${AEGIS_DIR}/aegis_inference.py \
--params ${AEGIS_DIR}/../aegis_inference_config.yml \
--images ${AEGIS_OUTPUT_DIR} \
--outputdir ${AEGIS_OUTPUT_DIR}

echo "Processing Complete"