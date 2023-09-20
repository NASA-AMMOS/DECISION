QUEUE_URL="https://sqs.us-east-1.amazonaws.com/295293350525/terraform-20230919220938849500000002"
MESSAGE_BODY="{\"task\":\"run_payload\"}"
# Post the message to SQS
aws sqs send-message --queue-url "$QUEUE_URL" --message-body "$MESSAGE_BODY" && exit 0 || exit 1