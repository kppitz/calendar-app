import boto3, sys, datetime as dt
sys.path.append('../')


client = boto3.client('cloudwatch', region_name='us-east-1')
logs = boto3.client('logs', region_name='us-east-1')

class LogWrapper:

    def add_log(log_group, log_stream, log_msg):
        response = logs.put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[
                {
                    'timestamp': int(dt.datetime.now().timestamp()*1000),
                    'message': str(log_msg)
                },
            ],
        )
        return response

    def create_log_group(log_group_name):
        return logs.create_log_group(logGroupName=log_group_name)
     
    def create_log_stream(log_group_name, log_stream_name):
       return logs.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)