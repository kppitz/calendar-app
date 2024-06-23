import sys
sys.path.append('../../')
from src.wrappers.sqs_wrapper import SqsWrapper as sqs
from src.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from src.wrappers.s3_wrapper import s3Wrapper as s3

def export_calendar():
    table = ddb.get_table("calendar-table")
    bucket = "calendar-cache"
    bucket_prefix = "kpitz-calendar-app/calendar/"
    response = ddb.cache_to_s3(table, bucket, bucket_prefix)
    return response

def process_status(status):
    response = "processing"
    if (status):
        response = "message received"
        operation = status['operation']
        status = status['status']
        if (operation == "exit"):
            response = "shutdown"
        elif (status == "success"):
            if(operation == "create" or operation == "delete" or operation == "update"):
                #export updated table to s3
                try:
                    export_response = export_calendar()
                    print("exported calendar to s3")
                except:
                    print("failed to export calendar to s3")
        print(status)
    return response

def calendar_handler():
    status_queue = sqs.get_queue("calendar-status-queue")
    status_response = "listening"

    print("connected to calendar status queue")

    while (status_response != "shutdown"):
        status_body = sqs.receive_messages(status_queue)

        if (status_body):
            print(status_body)
            status_response = process_status(status_body)

if __name__ == "__main__":
    calendar_handler()