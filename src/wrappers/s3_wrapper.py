import boto3, hashlib

s3 = boto3.client('s3')

class s3Wrapper():
    def cache_event(event_id):
        bucket = "calendar-event-cache"
        response = s3.put_object(Bucket=bucket, Key=event_id)

    def event_exists(event_id):
        bucket = "calendar-event-cache"
        try:
            s3.get_object(Bucket=bucket, Key=event_id)
            return True
        except:
            return False

    def delete_from_cache(event_id):
        bucket = "calendar-event-cache"
        response = s3.delete_object(Bucket=bucket, Key=event_id)

    def get_event_id(event_name, event_date):
        return str(hashlib.sha1(''.join([event_name, event_date]).encode()).hexdigest())