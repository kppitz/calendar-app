import sys, datetime as dt
sys.path.append('../../')
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.logs_wrapper import LogWrapper as log

log_group_name = '/calendar/calendar-handler'
log_stream_name = "calendar-handler-execution/" + str(dt.datetime.now().timestamp())

def export_calendar():
    table = ddb.get_table("calendar-table")
    bucket = "calendar-exports-cache"
    #print("ready to export")
    ddb.export_to_s3(table, bucket)

def process_status(calendar_status):
    response = "processing"
    if (calendar_status):
        response = "message processed"
        operation = calendar_status['operation']
        status = calendar_status['status']
        if (operation == "exit"):
            response = "shutdown"
            log.add_log(log_group_name, log_stream_name, "processing shutdown")
            print("shutting down")
        elif (status == "success"):
            status_id = calendar_status['request_details']['event_id']
            if (operation == "replace"):
                status_id = calendar_status['request_details']['new_event_id']
            print("calendar operation: " + operation + ", event id: " + status_id + ", status: " + status)
            log.add_log(log_group_name, log_stream_name, ("calendar operation: " + operation + ", event id: " + status_id + ", status: " + status))
            if(operation == "create" or operation == "delete" or operation == "update" or operation == "replace"):
                #export updated table to s3
                print()
                try:
                    #export_calendar()
                    print("exported calendar to s3")
                    log.add_log(log_group_name, log_stream_name, "exported calendar to s3")
                except Exception as error:
                    print("failed to export calendar to s3")
                    log.add_log(log_group_name, log_stream_name, ("failed to export calendar to s3: " + error))
    #print(status)
    return response

def calendar_handler():
    #log_group = log.create_log_group(log_group_name)
    log_stream = log.create_log_stream(log_group_name, log_stream_name)

    status_queue = sqs.get_queue("calendar-status-queue")
    status_response = "listening"

    log.add_log(log_group_name, log_stream_name, "connected to calendar status queue")
    print("connected to calendar status queue")
    print()

    while (status_response != "exit"):
        status_body = sqs.receive_messages(status_queue)

        if (status_body):
            #print(status_body)
            log.add_log(log_group_name, log_stream_name, ("received message: " + str(status_body)))
            status_response = process_status(status_body)
            log.add_log(log_group_name, log_stream_name, status_response)

if __name__ == "__main__":
    calendar_handler()