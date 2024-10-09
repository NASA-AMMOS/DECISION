# DECISION source code
export DECISION_DIR=${PWD}

# AEGIS source code
export AEGIS_DIR=${DECISION_DIR}/OSIA/aegis_rockster_server/aegis_rockster_server

# Set env vars below for use within acme_docker_trigger.sh
export CONTAINER_ID=aegis_rockster_server
export DATA_DIR=${DECISION_DIR}/data/AEGIS_Demo_Data

# Datetime for current run
export DATETIME=$1

export PORT=7625

echo "Looking for a container on port: ${PORT}"
ID=$(\
docker container ls --format="{{.ID}}\t{{.Ports}}" |\
grep ${PORT} |\
awk '{print $1}')
echo "Found Container ID: ${ID}"
echo "Stopping and removing it"
docker container stop ${ID} && docker container rm ${ID}

echo "Starting Server"

docker run -itd --rm -p ${PORT}:${PORT} ${CONTAINER_ID} 

sleep 5

echo "Running dakota"

dakota -error ${DECISION_DIR}/runs/${DATETIME}/dakota.out -i ${DECISION_DIR}/dakota/AEGIS/local/dakota.in > ${DECISION_DIR}/runs/${DATETIME}/dakota.out