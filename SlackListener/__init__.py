import json
import logging

import azure.functions as func


def main(req: func.HttpRequest, queuemessage: func.Out[str]) -> func.HttpResponse:
    logging.info("SlackListener HTTP trigger function processed a request.")

    name = req.params.get('name')

    if name:
        # Purely for testing that the Azure Function is running.
        logging.info("HTTP request URL contains a parameter called 'name'.")

        # Testing queue functionality
        queuemessage.set(f"Test Message. Name: {name}")

        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")

    else:
        logging.info("Parsing HTTP requests body into JSON.")

        # Parse requests body into JSON
        # https://stackoverflow.com/questions/64717762/how-to-trigger-a-azure-function-with-parameters-from-a-post-request
        req_body_bytes = req.get_body()
        logging.info(f"Request Bytes: {req_body_bytes}")
        req_body = req_body_bytes.decode("utf-8")
        logging.info(f"Request String: {req_body}")

        if req_body:
            req_body_json = json.loads(req_body)
            logging.info(f"Request JSON: {req_body_json}")
        else:
            req_body_json = {}

        # Case 1: this is a URL verification, not a notification from the Event API
        if 'challenge' in req_body_json and 'type' in req_body_json:
            logging.info("Extracting URL verification challenge.")

            challenge = req_body_json["challenge"]
            type = req_body_json["type"]

            logging.info(f"Challenge: {challenge}")
            logging.info(f"Type: {type}")

            # URL verification
            if type == 'url_verification':
                return func.HttpResponse(body=challenge,
                                        status_code=200)
            else:
                logging.error(f'URL verification failed. Expected type: url_verification. Actual type: {type}')
        
        # Case 2: this is a notification from the Event API
        else:
            logging.info("Storing information into queue.")

            # Write JSON payload to an Azure Storage Queue, so a separate Azure Function
            # can pick up the message, process it accordingly, and if applicable send an
            # API call to Slack
            queuemessage.set(json.dumps(req_body_json))

            logging.info("Sending confirmation to respond to the event request.")
            # Send immediate confirmation response to each event request
            # https://api.slack.com/apis/connections/events-api#prepare
            return func.HttpResponse(
                status_code=200
            )

