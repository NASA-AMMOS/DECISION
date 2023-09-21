QUEUE_URL="https://sqs.us-east-1.amazonaws.com/295293350525/terraform-20230919220938849500000002"
MESSAGE_BODY="{\"task\":\"run_payload\"}"
TARGET_FILE="/efs/data/ACME_Demo_Data/ACME_eval_logs_master/acme_eval_sweep_verbose.csv"
WAIT_TIME=3600  # 1 hour in seconds
CHECK_INTERVAL=10  # Check every 10 seconds

# Post the message to SQS
rm -rf /efs/data/ACME_Demo_Data/ACME_eval_logs_master/*
aws sqs send-message --queue-url "$QUEUE_URL" --message-body "$MESSAGE_BODY"

# Wait for the file to appear or timeout
start_time=$(date +%s)
while [[ ! -f "$TARGET_FILE" ]]; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [[ $elapsed_time -ge $WAIT_TIME ]]; then
        echo "Timeout waiting for the file."
        exit 1
    fi

    sleep $CHECK_INTERVAL
done

echo "File found!"
exit 0