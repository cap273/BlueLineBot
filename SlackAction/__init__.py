import logging
import os
import json

import azure.functions as func
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def main(msg: func.QueueMessage) -> None:

    # Parse message from Azure Storage Queue into JSON
    req_body = msg.get_body().decode('utf-8')
    logging.info('SlackAction queue trigger function processed a queue item: %s',
                 req_body)

    if req_body:
        req_body_json = json.loads(req_body)
        logging.info(f"Request JSON: {req_body_json}")
    else:
        req_body_json = {}

    # Acquire the application token for authentication to Slack, and 
    # get the Slack channel ID
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    channel_id = os.environ.get("Slack_Channel_ID")

    # Initialize Slack Web Client app using Slack SDK
    client = WebClient(token=slack_token)

    # If the message in the Azure Storage Queue is an event
    # received as a JSON payload from the Slack Event API, process it
    if ('event' in req_body_json and 
        'type' in req_body_json['event'] and 
        req_body_json['event']['type'] == 'message'):

        logging.info('SlackAction: Processing a message...')

        timestamp = req_body_json["event"]["ts"]

        # Find the text of the Slack message
        if 'text' in req_body_json["event"]:
            text = req_body_json["event"]["text"]
            text = text.lower()
        else:
            logging.error((f"Error: the value for the message's text was not found"))

        # If anything related to ORD appears in the text
        # of the Slack message, react with a train emoji
        if text and ("ord" in text or
            "ohare" in text or
            "o'hare" in text):

            logging.info(f"Message text: {text}")
            logging.info(f"Timestamp: {timestamp}")
            logging.info('Matching pattern found. Reacting...')

            try:
                response = client.reactions_add(
                    channel=channel_id,
                    name='train2',
                    timestamp=timestamp
                )
                logging.info(response)

            except SlackApiError as e:
                logging.error((f"Error posting message: {e}"))
        
        else:
            logging.info('No matching pattern found.')
    
    else:
        logging.info('SlackAction: The event received was not a message')