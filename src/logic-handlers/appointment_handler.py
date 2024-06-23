import sys, datetime as dt
sys.path.append('../../')
from src.wrappers.sqs_wrapper import SqsWrapper as sqs
from src.wrappers.sns_wrapper import SnsWrapper as sns
from src.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from src.wrappers.s3_wrapper import s3Wrapper as s3
from src.definitions.calendar_request import Payload

def add_appt(appt):
    table = ddb.get_table('calendar-table')
    table_item = {
        'event_id' : appt['event_id'],
        'event_name' : appt['event_name'],
        'date' : appt['event_date'],
        'start_time' :  appt['event_start'],
        'end_time' : appt['event_end'],
        'description' : appt['event_descrip'],
        'create_time' : str(dt.datetime.now())
    }
    response = ddb.add_item(table, table_item)
    s3.update_cache(s3, "create", appt['event_id'])
    return response

def update_appt(appt):
    table = ddb.get_table('calendar-table')
    table_item = {
        'event_id' : appt['event_id'],
        'event_name' : appt['event_name'],
        'date' : appt['event_date'],
        'start_time' :  appt['event_start'],
        'end_time' : appt['event_end'],
        'description' : appt['event_descrip'],
        'update_time' : str(dt.datetime.now())
    }
    response = ddb.update_item(table, table_item)
    return response

def replace_appt(appt):
    table = ddb.get_table('calendar-table')
    table_item = {
        'event_id' : appt['new_event_id'],
        'event_name' : appt['event_name'],
        'date' : appt['event_date'],
        'start_time' :  appt['event_start'],
        'end_time' : appt['event_end'],
        'description' : appt['event_descrip'],
        'replace_time' : str(dt.datetime.now())
    }
    response = ddb.replace_item(table, appt['event_id'], table_item)
    s3.update_cache(s3, "replace", appt['event_id'], appt['new_event_id'])
    return response

def delete_appt(appt):
    table = ddb.get_table('calendar-table')
    response = ddb.delete_item(table, appt['event_id'])
    s3.update_cache(s3, "delete", appt['event_id'])
    return response

def process_request(request):
    status = "processing"
    #add to notification queue
    if(request):
        print()
        print("calendar request processed")

        operation = request['operation']
        print(operation)

        if (operation == "exit"):
            response = "shutdown"
        elif (operation == "create"):
            #add appt to db
            print()
            try:
                add_response = add_appt(request['event_details'])
                print(add_response)
                status = "success"
            except:
                status = "failure"
        elif (operation == "update"):
            #update appt in db
            print()
            try:
                update_response = update_appt(request['event_details'])
                print(update_response)
                status = "success"
            except:
                status = "failure"
        elif (operation == "repalce"):
            #replace appt in db (delete then put)
            try:
                replace_response = replace_appt(request['event_details'])
                print(replace_response)
                status = "success"
            except:
                status = "failure"
        elif (operation == "delete"):
            #delete appt in db
            try:
                delete_response = delete_appt(request['event_details'])
                print(delete_response)
                status = "success"
            except:
                status = "failure"
        request_status = {
            'operation': operation,
            'status' : status,
            'request_details': request['event_details']
        }
    return request_status

def update_status(status, topic):
        status_payload = sqs.generate_payload("Update Status", status, "status")
        response = sns.publish(topic, status_payload)
        print()
        print("sent message to status queue")
        print(response)
        return response


def appt_handler():
    #setup for status queue
    status_queue = sqs.get_queue("calendar-status-queue")
    calendar_status_topic = sns.create_topic("calendar-status-topic")
    sqs.add_access_policy(status_queue, calendar_status_topic)
    calendar_status_subscription = sns.subscribe_to_topic(calendar_status_topic, status_queue)

    request_queue = sqs.get_queue("calendar-request-queue")
    response = "listening"

    print("connected to calendar request queue")
    print()

    while (response != "shutdown"):
        request_body = sqs.receive_messages(request_queue)

        if(request_body):
            print(request_body)
            request_response = process_request(request_body)
            status_response = update_status(request_response, calendar_status_topic)
        break


if __name__ == "__main__":
    appt_handler()