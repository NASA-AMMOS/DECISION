#######################################
# Insert dakota inputs into AEGIS config template
echo "Preparing dakota inputs with dprepro; params input at: ${1}"
echo $PWD
dprepro $1 aegis_config.template aegis_config.yml

#######################################
# AEGIS Processing and Eval

export AEGIS_OUTPUT_DIR=${PWD}/aegis_output/
mkdir $AEGIS_OUTPUT_DIR

echo "Executing aegis_test.py ..."

# Mount DATA_DIR as read only

python ${AEGIS_DIR}/aegis_test.py \
--params ${PWD}/aegis_config.yml \
--images ${DATA_DIR}/tmp/ \
--labels ${DATA_DIR}/labels/ \
--outputdir ${AEGIS_OUTPUT_DIR} > dakota.out

#######################################
# Exporting AEGIS results into dakota format
echo "Exporting dakota results. Input at: ${1}; output at ${2}"
python aegis_output_writer.py --dakota_input $1 --dakota_output $2 --aegis_output_dir "${AEGIS_OUTPUT_DIR}" > dakota.out
