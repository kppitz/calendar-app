import sys, datetime as dt
sys.path.append('../../')
from config.definitions.calendar_service import CalendarService as calendar
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.logs_wrapper import LogWrapper as log

log_group_name = '/calendar/calendar-handler'
log_stream_name = "calendar-handler-execution/" + str(dt.datetime.now().timestamp())

def calendar_handler(event, context):
    #log_group = log.create_log_group(log_group_name)
    #log_stream = log.create_log_stream(log_group_name, log_stream_name)
    #log.add_log(log_group_name, log_stream_name, ("incoming calendar-handler event: "+ event))

    calendar_status = calendar.process_status(event)

    #log.add_log(log_group_name, log_stream_name, ("calendar status: "+calendar_status) )
    # status_queue = sqs.get_queue("calendar-status-queue")
    # status_response = "listening"

    # #log.add_log(log_group_name, log_stream_name, "connected to calendar status queue")
    # logger.info("connected to calendar status queue")
    # print()

    # while (status_response != "exit"):
    #     status_body = sqs.receive_messages(status_queue)

    #     if (status_body):
    #         #print(status_body)
    #         #log.add_log(log_group_name, log_stream_name, ("received message: " + str(status_body)))
    #         status_response = calendar.process_status(status_body)
    #         #log.add_log(log_group_name, log_stream_name, status_response)