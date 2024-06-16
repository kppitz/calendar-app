#server.py
from flask import Flask, request, jsonify
import boto3

sqs = boto3.resource('sqs')

# Initiating a Flask application
app = Flask(__name__)

# The endpoint of our flask app
@app.route(rule="/", methods=["GET", "POST"])
def handle_request():
    # Get the queue
    queue = sqs.get_queue_by_name(QueueName='test')

    # The GET endpoint
    if request.method == "GET":
        return "This is the GET Endpoint of flask API."
    
    # The POST endpoint
    if request.method == "POST":
        # accesing the passed payload
        payload = request.get_json()
        # capitalizing the text
        cap_text = payload['text'].upper()
        # Creating a proper response
        response = {'cap-text': cap_text}
        # return the response as JSON
        return jsonify(response)
    
    # Create a new message
    response = queue.send_message(MessageBody='world')

    # The response is NOT a resource, but gives you a message ID and MD5
    print(response.get('MessageId'))
    print(response.get('MD5OfMessageBody'))

# Running the API
if __name__ == "__main__":
    # Setting host = "0.0.0.0" runs it on localhost
    app.run(host="0.0.0.0", debug=True)

