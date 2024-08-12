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

class ClientService :

    def create_event(event_contents):
        #create event parameters here
        print("Create calendar event")
        print()
        operation = "create"
        event_name = event_contents["event_name"]
        event_date = event_contents["event_date"]
        event = {
            'event_name' : event_name,
            'event_date' : event_date,
            'event_start' :  event_contents["event_start"],
            'event_end' : event_contents["event_end"],
            'event_descrip' : event_contents["event_descrip"],
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

    def get_event(event_contents):
        #get event parameters here
        print("Get calendar event details")
        print()
        # event_name = input("Enter event name: ")
        # event_date = input("Enter event date in mm-dd-yyyy format: ")
        operation = "get"
        event_name = event_contents["event_name"]
        event_date = event_contents["event_date"]
        event = {
            'event_name' : event_name,
            'event_date' : event_date
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

    def update_event(event_contents):
        #update event parameters here
        print("Update calendar event")
        print()
        operation = "update"
        event_name = event_contents["event_name"]
        event_date = event_contents["event_date"]
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
                new_event_name = event_contents["new_event_name"]
                new_event_date = event_contents["new_event_date"]

                new_event_id = s3.get_event_id(new_event_name, new_event_date)
                event = {
                    'event_id' : event_id,
                    'event_name' : new_event_name,
                    'event_date' : new_event_date,
                    'event_start' :  event_contents["new_event_start"],
                    'event_end' : event_contents["new_event_end"],
                    'event_descrip' : event_contents["new_event_descrip"],
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

    def delete_event(event_contents):
        #delete event parameters here
        print("Delete calendar event")
        print()
        operation = "delete"
        event_name = event_contents["event_name"]
        event_date = event_contents["event_date"]
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

    def process_client_request(client_request_file):
        #processes s3 bucket file with client response
        file_name = client_request_file["s3"]["object"]["key"]
        file_contents = s3.read_file(file_name)

        action = file_contents["operation"]
        event_status = "idle"

        #routes to correct event request validation
        if (action == "create"):
            log.add_log(log_group_name, log_stream_name, "create event request")
            event = ClientService.create_event(file_contents)
            event_status = event["operation_status"]
        elif (action == "get"):
            log.add_log(log_group_name, log_stream_name, "get event request")
            event = ClientService.get_event(file_contents)
            event_status = event["operation_status"]
        elif(action == "update"):
            log.add_log(log_group_name, log_stream_name, "update event request")
            event = ClientService.update_event(file_contents)
            event_status = event["operation_status"]
        elif(action == "delete"):
            log.add_log(log_group_name, log_stream_name, "delete event request")
            event = ClientService.delete_event(file_contents)
            event_status = event["operation_status"]
        elif(action == "exit"):
            log.add_log(log_group_name, log_stream_name, "exit request")
            run_type = "exit"
            event = {'operation_status': "in progress", 'event_msg':{'operation': "exit"}}
            event_status = event['operation_status']
        else:
            print("Action input not recognized. Please enter a valid action.")

        return event