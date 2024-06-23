import boto3, sys
from redis import Redis
sys.path.append('../')
from src.wrappers.sqs_wrapper import SqsWrapper as sqs
from src.wrappers.sns_wrapper import SnsWrapper as sns
from src.wrappers.s3_wrapper import s3Wrapper as s3
from src.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from src.definitions.calendar_request import Payload
from src.definitions.calendar_operations import Operation

client = boto3.client('cloudwatch')

def create_event():
    #create event parameters here
    print("Create calendar event")
    print()
    event_name = input("Enter event name: ")
    event_date = input("Enter event date: ")
    event_start = input("Enter event start time: ")
    event_end = input("Enter event end time: ")
    event_descrip = input("Enter event description: ")
    print()
    event_id = s3.get_event_id(event_name, event_date)

    #validate input
    if (not s3.event_exists(event_id)):
        event = {
            'event_id' : event_id,
            'event_name' : event_name,
            'event_date' : event_date,
            'event_start' :  event_start,
            'event_end' : event_end,
            'event_descrip' : event_descrip
        }

        print("The event id is: " + event_id)

        create_event = {'operation_status': "in progress", "event_msg":{'operation': "create", 'event_details': event}}
        return create_event
    else:
        print("""Cannot create. An event with that name and date already exists. /n
        You can update the existing event or create a new event with a different name or date.""")
        create_event = {'operation_status': "fail"}
    
    return create_event

def get_event():
    #get event parameters here
    print("Get calendar event details")
    print()
    event_name = input("Enter event name: ")
    event_date = input("Enter event date: ")
    event_id = s3.get_event_id(event_name, event_date)

    if s3.event_exists(event_id):
        event_details = ddb.get_item('calendar-table', event_id)
        print(event_details)
        get_event = {'operation_status': "success"}
    else:
        print("Cannot get event details. Calendar event with that name and date does not exist.")
        get_event = {'operation_status': "fail"}

    return get_event

def update_event():
    #update event parameters here
    print("Update calendar event")
    print()
    event_name = input("Enter event name: ")
    event_date = input("Enter event date: ")
    print()
    event_id = s3.get_event_id(event_name, event_date)

    #check if event id already 
    if s3.event_exists(event_id):
        new_event_name = input("Enter updated event name: ")
        new_event_date = input("Enter updated event date: ")
        new_event_start = input("Enter updated event start time: ")
        new_event_end = input("Enter updated event end time: ")
        new_event_descrip = input("Enter updated event description: ")
        new_event_id = s3.get_event_id(event_name, event_date)
        event = {
            'event_id' : event_id,
            'event_name' : new_event_name,
            'event_date' : new_event_date,
            'event_start' :  new_event_start,
            'event_end' : new_event_end,
            'event_descrip' : new_event_descrip
        }
        if(new_event_id != event_id):
            #replace event
            operation = "replace"
            event['new_event_id'] = new_event_id

        else:
            #update event
            operation = "update"
        
        update_event = {'operation_status': "in progress", 'event_msg':{'operation': operation, 'event_details': event}}
    else:
        print("Cannot update. Calendar event with that name and date does not exist.")
        update_event = {'operation_status': "fail"}
    
    return update_event

def delete_event():
    #delete event parameters here
    print("Delete calendar event")
    print()
    event_name = input("Enter event event name: ")
    event_date = input("Enter event date: ")
    print()
    event_id = s3.get_event_id(event_name, event_date)

    if (s3.event_exists(event_id)):
        event = {
            'event_id' : event_id
        }
        delete_event = {'operation_status': "in progress", 'event_msg':{'operation': "delete", 'event_details': event}}
    else:
        print("Cannot delete. Calendar event with that name and date does not exist.")
        delete_event = {'operation_status':"fail"}

    return delete_event

def client():
    run_type = "start"
    event = "start"

    #run setup
    calendar_request_queue = sqs.get_queue("calendar-request-queue")
    calendar_request_topic = sns.create_topic("calendar-request-topic")
    sqs.add_access_policy(calendar_request_queue, calendar_request_topic)
    calendar_request_subscription = sns.subscribe_to_topic(calendar_request_topic, calendar_request_queue)


    print("Welcome to your personal calendar!")

    while (run_type != "exit"):

        print("Enter info (i) for menu of calendar action, or enter your request action now.")
        action = input("request: ")
        if (action not in Operation.values()):
            print("Action input not recognized. Please enter a valid action.")
        else:
            if(action == Operation["info"]):
                #show menu of operations
                print("Calendar Actions")
                print("info (i): lists menu of calendar actions")
                print()
                print("create (c): create an event to add to calendar")
                print("search/get (g): get calendar event details")
                print("edit/update (u): update an existing calendar event")
                print("delete (d): delete an existing calendar event")
                print("exit (e): leave the calendar application")
                print()

            elif (action == Operation["create"]):
                event = create_event()
                event_msg = event["event_msg"]
                event_status = event["operation_status"]
            elif (action == Operation["get"]):
                event = get_event()
            elif(action == Operation["update"]):
                event = update_event()
                event_msg = event["event_msg"]
                event_status = event["operation_status"]
            elif(action == Operation["delete"]):
                event = delete_event()
                event_msg = event["event_msg"]
                event_status = event["operation_status"]
            elif(action == Operation["exit"]):
                event_msg = {'operation': "exit"}
                run_type = "exit"
            else:
                print("Action input not recognized. Please enter a valid action.")

            if (event_status != "fail"):
                if(event_status == "in progress"):
                    payload = sqs.generate_payload("Calendar Request", event_msg, "request")
                    print(payload)

                    calendar_request_response = sns.publish(calendar_request_topic, payload)
                    #print(calendar_request_response["MessageId"])
                print()



# Running the client
if __name__ == "__main__":
    client()