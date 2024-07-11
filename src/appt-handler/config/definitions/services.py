import re
from dateutil import parser

time_format = r'((1[0-2]|0?[1-9]):([0-5][0-9]) ?([AaPp][Mm]))'

def validate_event_input(event_input):
    if (len(event_input['event_name']) == 0 or 
        len(event_input['event_date']) == 0 or
        len(event_input['event_start']) == 0 or 
        len(event_input['event_end']) == 0):
        #mandatory fields are empty
        return False
    try:
        (parser.parse(event_input['event_date']))
    except:
        #event date format is invalid
        return False
    if(not (re.match(time_format, event_input['event_start'])) or not (re.match(time_format, event_input['event_end']))):
        # event start/end times are invalid formats
        return False
    return True

def validate_event_key_input(event_input):
    if (len(event_input['event_name']) == 0 or 
        len(event_input['event_date']) == 0):
        #mandatory fields are empty
        return False
    try:
        (parser.parse(event_input['event_date']))
    except:
        #event date format is invalid
        return False
    return True