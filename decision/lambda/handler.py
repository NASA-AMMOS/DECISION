import json
import boto3

# Initialize ECS client
ecs_client = boto3.client('ecs')

def lambda_handler(event, context):
    # Parse the SQS message
    for record in event['Records']:
        message_body = json.loads(record['body'])

        # Extracting elements from the message
        task_definition = message_body['task_definition']
        cluster_name = message_body['cluster_name']
        subnets = message_body['subnets']
        security_groups = message_body['security_groups']

        # Launch the ECS task with the provided details
        try:
            response = ecs_client.run_task(
                cluster=cluster_name,
                launchType='FARGATE',
                taskDefinition=task_definition,
                count=1,
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': subnets,
                        'securityGroups': security_groups,
                        'assignPublicIp': 'ENABLED'
                    }
                }
            )
            print(f"Task launched with response: {response}")

        except Exception as e:
            print(f"Error launching ECS task: {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }