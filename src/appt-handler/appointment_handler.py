import sys, datetime as dt, json, logging
sys.path.append('../../')
from config.definitions.appointment_service import AppointmentService as appt
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.sns_wrapper import SnsWrapper as sns
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.s3_wrapper import s3Wrapper as s3
from config.wrappers.logs_wrapper import LogWrapper as log

log_group_name = '/calendar/appointment-handler'
log_stream_name = "appt-handler-execution/" + str(dt.datetime.now().timestamp())
sqs_url = "https://sqs.us-east-1.amazonaws.com/381492094663/calendar-request-queue"

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

def appt_handler(event, context):
    #log_group = log.create_log_group(log_group_name)
    #log_stream = log.create_log_stream(log_group_name, log_stream_name)

    #setup for status queue
    status_queue = sqs.get_queue("calendar-status-queue")
    calendar_status_topic = sns.create_topic("calendar-status-topic")
    sqs.add_access_policy(status_queue, calendar_status_topic)
    calendar_status_subscription = sns.subscribe_to_topic(calendar_status_topic, status_queue)

    request_queue = sqs.get_queue("calendar-request-queue")
    operation = "listening"

    #log.add_log(log_group_name, log_stream_name, ("incoming appointment-handler event: " + event))
    logger.info("incoming appointment-handler event: " + str(event))

    message_request_body = json.loads(event['Records'][0]['body'])
    message_request_dict = json.loads(message_request_body['Message'])
    logger.info("appointment request body: " + str(message_request_dict))

    request_response = appt.process_request(message_request_dict)
    status_response = appt.update_status(request_response, calendar_status_topic)
    logger.info("appt update status response: " + str(status_response))

    delete_response = sqs.delete_message(sqs_url, event['Records'][0]['receiptHandle'])
    logger.info("deleted message from queue: " + str(delete_response))

    return request_response
