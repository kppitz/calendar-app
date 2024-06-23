import boto3, logging
from botocore.exceptions import ClientError

sns = boto3.resource('sns', region_name="us-east-1")
sns_client = boto3.client('sns', region_name="us-east-1")
logger = logging.getLogger(__name__)


class SnsWrapper:

    def create_topic(topic_name):
        topic = sns.create_topic(
            Name = topic_name + ".fifo",
            Attributes = {
                "FifoTopic": "True",
                "ContentBasedDeduplication": "True"
            }
        )
        return topic
    
    def subscribe_to_topic(topic, queue):
        subscription = topic.subscribe(
            Protocol = "sqs",
            Endpoint = queue.attributes["QueueArn"]
        )
        return subscription
    
    def publish(topic, payload):
        response = topic.publish(
            Subject = payload.subject,
            Message = payload.message,
            MessageGroupId = payload.group_id,
            # MessageStructure = 'json'
        )
        return response
    
    def unsubscribe_topic(subscription):
        subscription.delete()
    
    def delete_topic(topic):
        topic.delete()