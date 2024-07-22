class Payload():

    def __init__(self, subject, message, group_id):
        self.subject = subject
        self.message = message
        self.group_id = group_id

class CalendarRequest():
    def __init__(self, operation, ):
        self.operation = operation