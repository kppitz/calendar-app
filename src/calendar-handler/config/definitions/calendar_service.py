import sys, datetime as dt, logging
sys.path.append('../../')
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.logs_wrapper import LogWrapper as log

log_group_name = '/calendar/calendar-handler'
log_stream_name = "calendar-handler-execution/" + str(dt.datetime.now().timestamp())
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

class CalendarService:

    def export_calendar():
        table = ddb.get_table("calendar-table")
        bucket = "calendar-exports-cache"
        logger.info("ready to export")
        ddb.export_to_s3(table, bucket)

    def process_status(calendar_status):
        response = "processing"
        if (calendar_status):
            response = "message processed"
            operation = calendar_status['operation']
            status = calendar_status['status']
        if (operation == "exit"):
            response = "shutdown"
            #log.add_log(log_group_name, log_stream_name, "processing shutdown")
            logger.info("shutting down")
        elif (status == "success"):
            status_id = calendar_status['request_details']['event_id']
            if (operation == "replace"):
                status_id = calendar_status['request_details']['new_event_id']
            logger.info("calendar operation: " + operation + ", event id: " + status_id + ", status: " + status)
            #log.add_log(log_group_name, log_stream_name, ("calendar operation: " + operation + ", event id: " + status_id + ", status: " + status))
            if(operation == "create" or operation == "delete" or operation == "update" or operation == "replace"):
                #export updated table to s3
                print()
                try:
                    CalendarService.export_calendar()
                    logger.info("exported calendar to s3")
                    #log.add_log(log_group_name, log_stream_name, "exported calendar to s3")
                except Exception as error:
                    logger.info("failed to export calendar to s3")
                    #log.add_log(log_group_name, log_stream_name, ("failed to export calendar to s3: " + error))
        #print(status)
        return response
