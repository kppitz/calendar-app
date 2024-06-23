import boto3, datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
s3b = boto3.resource('s3')

class DdbWrapper:

    def cache_to_s3(table, bucket, bucket_prefix):
        response = dynamodb.export_table_to_point_in_time(
            TableArn = table.attributes['TableArn'],
            ExportTime=datetime(),
            S3Bucket = bucket,
            S3Prefix = bucket_prefix,
            S3SseAlgorithm='AES256',
            ExportFormat = 'DYNAMODB_JSON'
        )
        return response

    def add_item(table, item):
        response = table.put_item(Item=item)
        return response

    def update_item(table, item):
        response = table.put_item(Item=item)
        return response
    
    def replace_item(table, key, item):
        del_response = table.delete_item(Key=key)
        replace_response = table.put_item(Item=item)
        return replace_response

    def get_item(table, key):
        item = table.get_item(Key=key)
        return item
    
    def get_table(table_name):
        table = dynamodb.Table(table_name)
        return table

    def delete_item(table, key):
        response = table.delete_item(Key=key)
        return response