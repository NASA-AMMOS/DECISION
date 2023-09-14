QUEUE_URL="https://sqs.region.amazonaws.com/account-id/queue-name"
MESSAGE_BODY="Your message goes here"
# Post the message to SQS
aws sqs send-message --queue-url "$QUEUE_URL" --message-body "$MESSAGE_BODY" && exit 0 || exit 1