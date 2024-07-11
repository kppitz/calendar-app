import boto3, datetime as dt

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
ddbclient = boto3.client('dynamodb', region_name='us-east-1')
s3b = boto3.resource('s3', region_name='us-east-1')

class DdbWrapper:

    def export_to_s3(table, bucket):
        ddbclient.export_table_to_point_in_time(
            TableArn = table.table_arn,
            S3Bucket = bucket,
            S3SseAlgorithm='AES256',
            ExportFormat = 'DYNAMODB_JSON'
        )

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

    def get_item(table_name, key):
        table = dynamodb.Table(table_name)
        item = table.get_item(Key=key)
        return item['Item']
    
    def get_table(table_name):
        table = dynamodb.Table(table_name)
        return table

    def delete_item(table, key):
        response = table.delete_item(Key=key)
        return response