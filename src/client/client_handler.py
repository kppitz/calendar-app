import sys, datetime as dt, time, json, logging
#sys.path.append('../')
from config.definitions.client_service import ClientService as client
from config.wrappers.sqs_wrapper import SqsWrapper as sqs
from config.wrappers.sns_wrapper import SnsWrapper as sns
from config.wrappers.s3_wrapper import s3Wrapper as s3
from config.wrappers.dynamodb_wrapper import DdbWrapper as ddb
from config.wrappers.logs_wrapper import LogWrapper as log
from config.definitions.calendar_operations import Operation
import config.definitions.services as service

log_group_name = '/calendar/client-handler'
log_stream_name = "client-handler-execution/" + str(dt.datetime.now().timestamp())
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)


def client_handler(event, context):
    # TODO implement
    run_type = "start"
    event_status = "start"

    #log_stream = log.create_log_stream(log_group_name, log_stream_name)

    #run setup
    calendar_request_queue = sqs.get_queue("calendar-request-queue")
    calendar_request_topic = sns.create_topic("calendar-request-topic")
    sqs.add_access_policy(calendar_request_queue, calendar_request_topic)
    calendar_request_subscription = sns.subscribe_to_topic(calendar_request_topic, calendar_request_queue)

    # log.add_log(log_group_name, log_stream_name, "Client executable started")
    logger.info("incoming client-handler event: " + str(event))
    logger.info("incoming s3 file: ", event['Records'][0]['s3'])
    
    client_request_event = client.process_client_request(event['Records'][0]['s3'])

    logger.info("client request event: " + str(client_request_event))
    return client_request_event
