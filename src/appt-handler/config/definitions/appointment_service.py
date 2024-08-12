import sys, datetime as dt, time
sys.path.append('../../')
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.sns_wrapper import SnsWrapper as sns
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.s3_wrapper import s3Wrapper as s3
from config.wrappers.logs_wrapper import LogWrapper as log

log_group_name = '/calendar/appointment-handler'
log_stream_name = "appt-handler-execution/" + str(dt.datetime.now().timestamp())

class AppointmentService:

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
                        add_response = AppointmentService.add_appt(request_details)
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
                        update_response = AppointmentService.update_appt(request_details)
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
                        replace_response = AppointmentService.replace_appt(request_details)
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
                        delete_response = AppointmentService.delete_appt(request_details)
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