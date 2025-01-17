import boto3, json, sys
sys.path.append('../../')
from config.definitions.calendar_request import Payload

sqs = boto3.resource('sqs', region_name="us-east-1")
sqs_client = boto3.client('sqs', region_name="us-east-1")

class SqsWrapper:

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

            #logger.info("received message")
            #print(message_body['Message'])

            message_body_dict = json.loads(message_body['Message'])

            message.delete()

            return message_body_dict

    def send_message(queue, message):
        response = queue.send_message(MessageBody=message)
        return response
    
    def delete_message(queue_url, receipt_handle):
        response = sqs_client.delete_message(QueueUrl=queue_url,ReceiptHandle=receipt_handle)
        return response

    def delete_queue(queue):
        queue.delete()

    def generate_payload(subject, message, group_id):
        #build calendar request payload
        payload = Payload(
            subject = subject,
            message = json.dumps(message),
            group_id = group_id
        )
        #logger.info("payload message: " + payload.message)
        return payload