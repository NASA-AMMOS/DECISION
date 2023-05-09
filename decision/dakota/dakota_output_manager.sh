echo "Dakota Output Manager Input Path: $1"
echo "Dakota Output Manager Output Path: $2"
python dakota/dakota_result_writer.py --dakota_input $1 --dakota_output $2 --acme_output_dir 'data/ACME_Demo_Data/ACME_eval_logs_master/'