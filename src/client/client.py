import sys, datetime as dt, time
#sys.path.append('../')
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.sns_wrapper import SnsWrapper as sns
from config.wrappers.s3_wrapper import s3Wrapper as s3
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.logs_wrapper import LogWrapper as log
from config.definitions.calendar_operations import Operation
import config.definitions.services as service

log_group_name = '/calendar/client'
log_stream_name = "client-execution/" + str(dt.datetime.now().timestamp())

def create_event():
    #create event parameters here
    print("Create calendar event")
    print()
    event_name = input("Enter event name: ")
    event_date = input("Enter event date in mm-dd-yyyy format: ")
    event_start = input("Enter event start time in hh:mm am/pm format: ")
    event_end = input("Enter event end time in hh:mm am/pm format: ")
    event_descrip = input("Enter event description: ")
    print()
    operation = "create"
    event = {
        'event_name' : event_name,
        'event_date' : event_date,
        'event_start' :  event_start,
        'event_end' : event_end,
        'event_descrip' : event_descrip,
        'create_time' : str(dt.datetime.now())
    }

    log.add_log(log_group_name, log_stream_name, ("create request input: " + str(event)))

    #validate input
    if (not service.validate_event_input(event)):
        print("Create event request format is invalid.")
        log.add_log(log_group_name, log_stream_name, "invalid request input")
        return {'operation_status': "fail"}
    else:
        event_id = s3.get_event_id(event_name, event_date)
        if (not s3.event_exists(event_id)):
            event['event_id'] = event_id
            print("The event id is: " + event_id)
            print("Create event in progress")
            operation_status = "in progress"
            log.add_log(log_group_name, log_stream_name, "create request in progress")
        else:
            print("""Cannot create. An event with that name and date already exists.\nYou can update the existing event or create a new event with a different name or date.""")
            operation_status = "fail"
            log.add_log(log_group_name, log_stream_name, "create request invalid, event already exists.")
    
    create_event = {'operation_status': operation_status, "event_msg":{'operation': operation, 'event_details': event}}
    return create_event

def get_event():
    #get event parameters here
    print("Get calendar event details")
    print()
    event_name = input("Enter event name: ")
    event_date = input("Enter event date in mm-dd-yyyy format: ")
    operation = "get"
    event = {
        'event_name': event_name,
        'event_date': event_date
    }

    log.add_log(log_group_name, log_stream_name, ("get request input: " + str(event)))

    if (not service.validate_event_key_input(event)):
        print("Invalid search input.")
        log.add_log(log_group_name, log_stream_name, "invalid request input")
        return {'operation_status': "fail"}
    else:
        event_id = s3.get_event_id(event_name, event_date)
        if s3.event_exists(event_id):
            get_key = {'event_id': event_id}
            event_details = ddb.get_item('calendar-table', get_key)
            print()
            print("calendar event details: ")
            print(event_details)
            operation_status = "success"
            log.add_log(log_group_name, log_stream_name, ("get event details: " + str(event_details)))
        else:
            print("Cannot get event details. Calendar event with that name and date does not exist.")
            log.add_log(log_group_name, log_stream_name, "Get request failed. Event does not exist.")
            operation_status = "fail"

        get_event = {'operation_status': operation_status, 'event_msg':{'operation':operation}}
        return get_event

def update_event():
    #update event parameters here
    print("Update calendar event")
    print()
    event_name = input("Enter event name: ")
    event_date = input("Enter event date in mm-dd-yyyy format: ")
    print()
    operation = "update"
    event = {
        'event_name': event_name,
        'event_date': event_date
    }

    log.add_log(log_group_name, log_stream_name, ("update request key input: " + str(event)))

    if (not service.validate_event_key_input(event)):
        print("Invalid update input.")
        log.add_log(log_group_name, log_stream_name, "invalid request input")
        return {'operation_status': "fail"}
    else:
        #check if event id already 
        event_id = s3.get_event_id(event_name, event_date)
        print
        if s3.event_exists(event_id):
            new_event_name = input("Enter updated event name: ")
            new_event_date = input("Enter updated event date in mm-dd-yyyy format: ")
            new_event_start = input("Enter updated event start time in hh:mm am/pm format: ")
            new_event_end = input("Enter updated event end time in hh:mm am/pm format: ")
            new_event_descrip = input("Enter updated event description: ")
            print()

            new_event_id = s3.get_event_id(new_event_name, new_event_date)
            event = {
                'event_id' : event_id,
                'event_name' : new_event_name,
                'event_date' : new_event_date,
                'event_start' :  new_event_start,
                'event_end' : new_event_end,
                'event_descrip' : new_event_descrip,
                'update_time' : str(dt.datetime.now())
            }
            #validate event input
            if (not service.validate_event_input(event)):
                print("Invalid update input.")
                log.add_log(log_group_name, log_stream_name, "invalid request input")
                return {'operation_status': "fail"}
            else:
                if(new_event_id != event_id):
                    #replace event
                    operation = "replace"
                    event['new_event_id'] = new_event_id
                    print("The new event id is: " + new_event_id)
                    print("Replace event in progress")
                    operation_status = "in progress"
                    log.add_log(log_group_name, log_stream_name, ("replace request input: " + str(event)))
                else:
                    #update event
                    operation = "update"
                    print("The event id is: " + event_id)
                    print("Update event in progress")
                    operation_status = "in progress"
                    log.add_log(log_group_name, log_stream_name, ("update request input: " + str(event)))
        else:
            print("Cannot update. Calendar event with that name and date does not exist.")
            log.add_log(log_group_name, log_stream_name, "Update request failed. Event does not exist")
            operation_status = "fail"
        
    update_event = {'operation_status': operation_status, 'event_msg':{'operation': operation, 'event_details': event}}
    
    return update_event

def delete_event():
    #delete event parameters here
    print("Delete calendar event")
    print()
    event_name = input("Enter event event name: ")
    event_date = input("Enter event date in mm-dd-yyyy format: ")
    print()
    operation = "delete"
    event = {
        'event_name': event_name,
        'event_date': event_date,
        'delete_time' : str(dt.datetime.now())
    }

    log.add_log(log_group_name, log_stream_name, ("delete request key input: " + str(event)))

    #validate input
    if (not service.validate_event_key_input(event)):
        print("Invalid delete input")
        log.add_log(log_group_name, log_stream_name, "invalid request input")
        return {'operation_status': "fail"}
    else:
        event_id = s3.get_event_id(event_name, event_date)
        if (s3.event_exists(event_id)):
            event['event_id'] = event_id
            print("Delete event in progress")
            operation_status = "in progress"
            log.add_log(log_group_name, log_stream_name, ("delete request input: " + str(event)))
        else:
            print("Cannot delete. Calendar event with that name and date does not exist.")
            log.add_log(log_group_name, log_stream_name, "Delete request failed. Event does not exist.")
            operation_status = "fail"

    delete_event = {'operation_status': operation_status, 'event_msg':{'operation': operation, 'event_details': event}}
    return delete_event

def client():
    run_type = "start"
    event_status = "start"

    #log_group = log.create_log_group(log_group_name)
    log_stream = log.create_log_stream(log_group_name, log_stream_name)

    #run setup
    calendar_request_queue = sqs.get_queue("calendar-request-queue")
    calendar_request_topic = sns.create_topic("calendar-request-topic")
    sqs.add_access_policy(calendar_request_queue, calendar_request_topic)
    calendar_request_subscription = sns.subscribe_to_topic(calendar_request_topic, calendar_request_queue)

    log.add_log(log_group_name, log_stream_name, "Client executable started")

    print("Welcome to your personal calendar!")

    while (run_type != "exit"):
        print()
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
                print("get/search (g): get calendar event details")
                print("update/replace (u): update an existing calendar event")
                print("delete (d): delete an existing calendar event")
                print("exit (e): leave the calendar application")
                print()

                event_status = "idle"

            elif (action == Operation["create"]):
                log.add_log(log_group_name, log_stream_name, "create event request")
                event = create_event()
                event_status = event["operation_status"]
            elif (action == Operation["get"]):
                log.add_log(log_group_name, log_stream_name, "get event request")
                event = get_event()
                event_status = event["operation_status"]
            elif(action == Operation["update"]):
                log.add_log(log_group_name, log_stream_name, "update event request")
                event = update_event()
                event_status = event["operation_status"]
            elif(action == Operation["delete"]):
                log.add_log(log_group_name, log_stream_name, "delete event request")
                event = delete_event()
                event_status = event["operation_status"]
            elif(action == Operation["exit"]):
                log.add_log(log_group_name, log_stream_name, "exit request")
                run_type = "exit"
                event = {'operation_status': "in progress", 'event_msg':{'operation': "exit"}}
                event_status = event['operation_status']
            else:
                print("Action input not recognized. Please enter a valid action.")

            if (event_status != "fail"):
                if(event_status == "in progress"):
                    event_msg = event["event_msg"]
                    log.add_log(log_group_name, log_stream_name, "calendar request payload message: " + str(event_msg))
                    payload = sqs.generate_payload("Calendar Request", event_msg, "request")
                    #print(payload)
                    log.add_log(log_group_name, log_stream_name, "calendar request payload: " + str(payload))
                    calendar_request_response = sns.publish(calendar_request_topic, payload)
                    #print(calendar_request_response["MessageId"])
                    log.add_log(log_group_name, log_stream_name, "sns publish response: " + str(calendar_request_response))
                    log.add_log(log_group_name, log_stream_name, "published message to calendar request queue")

                    if(run_type == "exit"):
                        print("shutting down")
                        time.sleep(5)
                print()

# Running the client
if __name__ == "__main__":
    client()