import sys, datetime as dt, logging, json
sys.path.append('../../')
from config.definitions.calendar_service import CalendarService as calendar
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.logs_wrapper import LogWrapper as log

log_group_name = '/calendar/calendar-handler'
log_stream_name = "calendar-handler-execution/" + str(dt.datetime.now().timestamp())
sqs_url = "https://sqs.us-east-1.amazonaws.com/381492094663/calendar-status-queue"

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

def calendar_handler(event, context):
    #log_group = log.create_log_group(log_group_name)
    #log_stream = log.create_log_stream(log_group_name, log_stream_name)

    logger.info("incoming calendar-handler event: "+ str(event))

    status_request_body = json.loads(event['Records'][0]['body'])
    status_request_dict = json.loads(status_request_body['Message'])
    logger.info("calendar status  body: " + str(status_request_dict))

    calendar_status = calendar.process_status(status_request_dict)
    logger.info(str(calendar_status))
    
    delete_response = sqs.delete_message(sqs_url, event['Records'][0]['receiptHandle'])
    logger.info("deleted message from queue: " + str(delete_response))

    return calendar_status