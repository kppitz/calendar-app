import sys, datetime as dt, time
sys.path.append('../../')
from src.wrappers.sqs_wrapper import SqsWrapper as sqs
from src.wrappers.sns_wrapper import SnsWrapper as sns
from src.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from src.wrappers.s3_wrapper import s3Wrapper as s3
from src.wrappers.logs_wrapper import LogWrapper as log

log_group_name = '/calendar/appointment-handler'
log_stream_name = "appt-handler-execution/" + str(dt.datetime.now().timestamp())

def add_appt(appt):
    table = ddb.get_table('calendar-table')
    table_item = {
        'event_id' : appt['event_id'],
        'event_name' : appt['event_name'],
        'date' : appt['event_date'],
        'start_time' :  appt['event_start'],
        'end_time' : appt['event_end'],
        'description' : appt['event_descrip']
    }
    response = ddb.add_item(table, table_item)
    log.add_log(log_group_name, log_stream_name, "Add Item: " + str(response))
    cache_response = s3.cache_event(appt['event_id'])
    log.add_log(log_group_name, log_stream_name, "Cache add event id: " + str(cache_response))
    return response

def update_appt(appt):
    table = ddb.get_table('calendar-table')
    table_item = {
        'event_id' : appt['event_id'],
        'event_name' : appt['event_name'],
        'date' : appt['event_date'],
        'start_time' :  appt['event_start'],
        'end_time' : appt['event_end'],
        'description' : appt['event_descrip']
    }
    response = ddb.update_item(table, table_item)
    log.add_log(log_group_name, log_stream_name, "Update Item: " + str(response))
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
    }
    replace_key = {'event_id': appt['event_id']}
    response = ddb.replace_item(table, replace_key, table_item)
    log.add_log(log_group_name, log_stream_name, "Replace Item: " + str(response))
    cache_response = s3.delete_from_cache(appt['event_id'])
    cache_response = s3.cache_event(appt['new_event_id'])
    log.add_log(log_group_name, log_stream_name, "Cache replace new event id: " + str(cache_response))
    return response

def delete_appt(appt):
    table = ddb.get_table('calendar-table')
    delete_key = {'event_id': appt['event_id']}
    response = ddb.delete_item(table, delete_key)
    log.add_log(log_group_name, log_stream_name, "Delete Item: " + str(response))
    cache_response = s3.delete_from_cache(appt['event_id'])
    log.add_log(log_group_name, log_stream_name, "Cache remove event id: " + str(cache_response))
    return response

def process_request(request):
    status = "processing"
    #add to notification queue
    if(request):
        operation = request['operation']
        if (operation == "exit"):
            status = "in progress"
            request_details = "shutdown"
            log.add_log(log_group_name, log_stream_name, "processing shutdown")
            print("shutting down")
        else:
            request_id = request['event_details']['event_id']
            if (operation == "replace"):
                request_id = request['event_details']['new_event_id']
            print("processing calendar " + operation + " operation for event id: " + request_id)
            log.add_log(log_group_name, log_stream_name, ("processing calendar " + operation + " operation for event id: " + request_id))
            if (operation == "create"):
                #add appt to db
                request_details = request['event_details']
                print()
                try:
                    add_response = add_appt(request_details)
                    #print(add_response)
                    status = "success"
                    log.add_log(log_group_name, log_stream_name, "Added event to db")
                except Exception as error:
                    status = "failure"
                    log.add_log(log_group_name, log_stream_name, ("Failed to add event to db: " + error))
            elif (operation == "update"):
                #update appt in db
                print()
                request_details = request['event_details']
                try:
                    update_response = update_appt(request_details)
                    #print(update_response)
                    status = "success"
                    log.add_log(log_group_name, log_stream_name, "Updated event in db")
                except Exception as error:
                    status = "failure"
                    log.add_log(log_group_name, log_stream_name, ("Failed to update event to db: " + error))
            elif (operation == "replace"):
                #replace appt in db (delete then put)
                request_details = request['event_details']
                try:
                    replace_response = replace_appt(request_details)
                    #print(replace_response)
                    status = "success"
                    log.add_log(log_group_name, log_stream_name, "Replaced event in db")
                except Exception as error:
                    status = "failure"
                    log.add_log(log_group_name, log_stream_name, ("Failed to replace event to db: " + error))
            elif (operation == "delete"):
                #delete appt in db
                request_details = request['event_details']
                try:
                    delete_response = delete_appt(request_details)
                    #print(delete_response)
                    status = "success"
                    log.add_log(log_group_name, log_stream_name, "Deleted event from db")
                except Exception as error:
                    status = "failure"
                    log.add_log(log_group_name, log_stream_name, ("Failed to delete event from db: " + error))
        request_status = {
            'operation': operation,
            'status' : status,
            'request_details': request_details
        }
    return request_status

def update_status(status, topic):
        log.add_log(log_group_name, log_stream_name, "calendar status payload message: " + str(status))
        status_payload = sqs.generate_payload("Update Status", status, "status")
        log.add_log(log_group_name, log_stream_name, "calendar status payload: " + str(status_payload))
        response = sns.publish(topic, status_payload)
        log.add_log(log_group_name, log_stream_name, "sns publish response: " + str(response))
        print()
        #print("sent message to status queue")
        log.add_log(log_group_name, log_stream_name, "sent message to calendar status queue")
        #print(response)
        return response


def appt_handler():
    #log_group = log.create_log_group(log_group_name)
    log_stream = log.create_log_stream(log_group_name, log_stream_name)

    #setup for status queue
    status_queue = sqs.get_queue("calendar-status-queue")
    calendar_status_topic = sns.create_topic("calendar-status-topic")
    sqs.add_access_policy(status_queue, calendar_status_topic)
    calendar_status_subscription = sns.subscribe_to_topic(calendar_status_topic, status_queue)

    request_queue = sqs.get_queue("calendar-request-queue")
    operation = "listening"

    log.add_log(log_group_name, log_stream_name, "connected to calendar request queue")

    print("connected to calendar request queue")
    print()

    while (operation != "exit"):
        request_body = sqs.receive_messages(request_queue)

        if(request_body):
            #print(request_body)
            log.add_log(log_group_name, log_stream_name, ("received request: " + str(request_body)))
            request_response = process_request(request_body)
            status_response = update_status(request_response, calendar_status_topic)
            operation = request_response['operation']


if __name__ == "__main__":
    appt_handler()