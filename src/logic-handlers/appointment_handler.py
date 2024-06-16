import boto3, json, sys, os
sys.path.append('../../')
from src.services.sqs_service import SqsService as sqs
from src.services.sns_service import SnsService as sns
from src.definitions.calendar_request import Payload

dynamodb = boto3.resource('dynamodb')
# sqs = boto3.resource('sqs')
# sns = boto3.resource('sns')

exit = False

# Get the queue
#request = sqs.get_queue_by_name(QueueName='calendar-requests')
request = sqs.get_queue("calendar-request-queue")

print("connected to queue")

request_body = sqs.receive_messages(request)

# for message in sqs.receive_message(request):
#     print("received message")
#     message_body = message['Message']
#     # message_body = json.loads(message.body)
#     print(message_body)

# Process messages by printing out body and optional author name
# for message in request.receive_messages(WaitTimeSeconds=5, MaxNumberOfMessages=1):

#     message_body = json.loads(message.body)

#     print("received message")

#     print(message_body['Message'])

#     # Let the queue know that the message is processed
#     #message.delete()

def process_request(request):
    if request == "test":
        return

def appt_handler():
    request = sqs.get_queue("calendar-request-queue")

    print("connected to queue")

    request_body = sqs.receive_messages(request)

    print(request_body)

if __name__ == "__main__":
    appt_handler()