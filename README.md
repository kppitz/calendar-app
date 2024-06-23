# calendar-app
AWS hosted calendar app to keep appointments

Components:
Client: this is an executable that the user interacts with, making requests to add to, update, delete items, and view the calendar

Appointment Handler: this executable manages the client requests and runs the appropriate logic in the backend

Calendar Handler: this executable listens for when the calendar state changes and caches the updated calendar to an s3 bucket for exporting

TO RUN:
Client: python calendar-app/src/client.py
Appointment Handler executable: python calendar-app/src/logic-handlers/appointment_handler.py
Calendar Handler: python calendar-app/src/logic-handlers/calendar_handler.py

