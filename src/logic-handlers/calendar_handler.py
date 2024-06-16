import boto3

dynamodb = boto3.resource('dynamodb')
sqs = boto3.resource('sqs')

# # Get the queue
# queue = sqs.get_queue_by_name(QueueName='calendar-queue')

# # Process messages by printing out body and optional author name
# for message in queue.receive_messages(MessageAttributeNames=['operation']):
#     if message.message_attributes is not None:
#         operation = message.message_attributes.get('operation').get('StringValue')

#     print("operation: ", operation)

#     calendar = dynamodb.Table('calendar-table')

#     appointment = calendar.put_item(
#         Item={}
#     )

#     print("Added appointment to calendar")

#     #send message to client via sns

#     # Let the queue know that the message is processed
#     message.delete()

def calendar_handler():
    request = sqs.get_queue("calendar-db-queue")

    print("connected to queue")

    request_body = sqs.receive_messages(request)

    print(request_body)

if __name__ == "__main__":
    calendar_handler()