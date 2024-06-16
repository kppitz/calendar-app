import boto3, json

sqs = boto3.resource('sqs', region_name="us-east-1")
sqs_client = boto3.client('sqs', region_name="us-east-1")

class SqsService:

    def create_queue(queue_name):
        queue = sqs.create_queue(QueueName=queue_name)
        return queue
    
    def add_access_policy(queue, topic):
        queue.set_attributes(
            Attributes={
                "Policy": json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "test-sid",
                                "Effect": "Allow",
                                "Principal": {"AWS": "*"},
                                "Action": "SQS:SendMessage",
                                "Resource": queue.attributes["QueueArn"],
                                "Condition": {
                                    "ArnLike": {"aws:SourceArn": topic.attributes["TopicArn"]}
                                },
                            }
                        ],
                    }
                )
            }
        )

    def get_queue(queue_name):
        return sqs.get_queue_by_name(QueueName=queue_name)

    def receive_messages(queue):
        for message in queue.receive_messages(WaitTimeSeconds=5, MaxNumberOfMessages=1):

            message_body = json.loads(message.body)

            print("received message")

            print(message_body['Message'])

            return message_body['Message']
        
        # Let the queue know that the message is processed
        #message.delete()

    def send_message(queue, message):
        response = queue.send_message(message)
        return response

    def delete_queue(queue):
        queue.delete()