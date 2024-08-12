import sys, datetime as dt, time
sys.path.append('../../')
from config.definitions.appointment_service import AppointmentService as appt
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.sns_wrapper import SnsWrapper as sns
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.s3_wrapper import s3Wrapper as s3
from config.wrappers.logs_wrapper import LogWrapper as log

log_group_name = '/calendar/appointment-handler'
log_stream_name = "appt-handler-execution/" + str(dt.datetime.now().timestamp())

def appt_handler(event, context):
    #log_group = log.create_log_group(log_group_name)
    log_stream = log.create_log_stream(log_group_name, log_stream_name)

    #setup for status queue
    status_queue = sqs.get_queue("calendar-status-queue")
    calendar_status_topic = sns.create_topic("calendar-status-topic")
    sqs.add_access_policy(status_queue, calendar_status_topic)
    calendar_status_subscription = sns.subscribe_to_topic(calendar_status_topic, status_queue)

    request_queue = sqs.get_queue("calendar-request-queue")
    operation = "listening"

    log.add_log(log_group_name, log_stream_name, ("incoming appointment-handler event: " + event))
    request_response = appt.process_request(event)
    status_response = appt.update_status(request_response, calendar_status_topic)

    log.add_log(log_group_name, log_stream_name, ("appt update status response: " + status_response))

    # log.add_log(log_group_name, log_stream_name, "connected to calendar request queue")

    # print("connected to calendar request queue")
    # print()

    # while (operation != "exit"):
    #     request_body = sqs.receive_messages(request_queue)

    #     if(request_body):
    #         #print(request_body)
    #         log.add_log(log_group_name, log_stream_name, ("received request: " + str(request_body)))
    #         request_response = process_request(request_body)
    #         status_response = update_status(request_response, calendar_status_topic)
    #         operation = request_response['operation']