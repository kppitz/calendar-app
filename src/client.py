import requests, json, enum, random, string
import logging
import boto3
from services.sqs_service import SqsService as sqs
from services.sns_service import SnsService as sns
from definitions.calendar_request import Payload

#sns = boto3.resource('sns', region_name="us-east-1")
#sqs = boto3.resource('sqs', region_name="us-east-1")

logger = logging.getLogger(__name__)

exit = False

def create_event():
    #create event parameters here
    print("Create calendar event")
    print()
    event_args = input("Enter arguments in this format: event-name, event-date, start-time, end-time, description")
    event_details = event_args.split(",")
    # event_name = input("Enter event name: ")
    # event_date = input("Enter event date: ")
    # event_start = input("Enter event start time: ")
    # event_end = input("Enter event end time: ")
    # event_details = input("Enter event description: ")
    #event_id = str(random.choices(string.ascii_uppercase + string.digits, k=7))

    event = dict(
        event_name = event_details[0],
        event_date = event_details[1],
        event_start = event_details[2],
        event_end = event_details[3],
        event_desrip = event_details[4]
    )

    return event

def get_search():
    #get event parameters here
    print("Get calendar event details")
    print()
    event_args = ("Enter event id: ")

    event = dict(
        event_id = event_args
    )

    return event

def update_event():
    #update event parameters here
    print("Update calendar event")
    print()
    event_args = input("Enter arguments in this format: event-id, event-name, event-date, start-time, end-time, description")
    event_details = event_args.split(",")

    event = dict(
        event_id = event_details[0],
        event_name = event_details[1],
        event_date = event_details[2],
        event_start = event_details[3],
        event_end = event_details[4],
        event_desrip = event_details[5]
    )

    return event

def delete_event():
    #delete event parameters here
    print("Delete calendar event")
    print()
    event_args = input("Enter arguments in this format: event-id")

    event = dict(
        event_id = event_args
    )

    return event

def generate_payload(payload_details):
    #build calendar request payload
    payload = Payload(
        subject = "Calendar Request",
        message = payload_details,
        group_id = "request"
    )
    return payload

def client():
    print("Welcome to your personal calendar!")

    run_type = input("run (client) or (cleanup): ")

    # while (not exit):
    #     print("Enter info (i) for menu of calendar action, or enter your request action now.")
    #     action = input("request: ")
    #     if(action == Operation.INFO):
    #         #show menu of operations
    #         print("Calendar Actions")
    #         print("info (i): lists menu of calendar actions")
    #         print()
    #         print("create (c): create an event to add to calendar")
    #         print("search/get (g): get calendar event details")
    #         print("edit/update (u): update an existing calendar event")
    #         print("delete (d): delete an existing calendar event")
    #         print("exit (e): leave the calendar application")
    #         print()

    #     elif (action == Operation.CREATE):
    #         event = create_event()
    #         generate_payload(event)
    #     elif (action == Operation.GET):
    #         event = get_search()
    #         generate_payload(event)
    #     elif(action == Operation.UPDATE):
    #         event = update_event()
    #         generate_payload(event)
    #     elif(action == Operation.DELETE):
    #         event = delete_event()
    #         generate_payload(event)
    #     elif(action == Operation.EXIT):
    #         break

    #     else:
    #         print("Action input not recognized. Please enter a valid action.")

    calendar_request_queue = sqs.create_queue("calendar-request-queue")

    calendar_request_topic = sns.create_topic("calendar-request-topic")

    sqs.add_access_policy(calendar_request_queue, calendar_request_topic)

    calendar_request_subscription = sns.subscribe_to_topic(calendar_request_topic, calendar_request_queue)

    payload = generate_payload("test")

    calendar_request_response = sns.publish(calendar_request_topic, payload)

    print(calendar_request_response["MessageId"])

    # # Create a new message
    # response = queue.send_message(MessageBody='boto3', MessageAttributes={
    #     'Author': {
    #             'StringValue': 'Daniel',
    #             'DataType': 'String'
    #         }
    #     })

    # # The response is NOT a resource, but gives you a message ID and MD5
    # print(response.get('MessageId'))
    # print(response.get('MD5OfMessageBody'))

    if(run_type == "cleanup"):
        #cleanup on exit
        # calendar_request_subscription.delete()
        # calendar_requests_topic.delete()
        # calendar_requests_queue.delete()
        sns.unsubscribe_topic(calendar_request_subscription)
        sns.delete_topic(calendar_request_topic)
        sqs.delete_queue(calendar_request_queue)

# Running the client
if __name__ == "__main__":
    client()