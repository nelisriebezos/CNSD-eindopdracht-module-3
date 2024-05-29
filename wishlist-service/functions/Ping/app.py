import json
from os import environ
import boto3
from aws_xray_sdk.core import patch_all
import logging

if 'DISABLE_XRAY' not in environ:
    patch_all()

event_bus = boto3.client('events')
logger = logging.getLogger()
logger.setLevel("INFO")


def lambda_handler(event, context):
    event = {
        'Source': 'user-context',
        'DetailType': 'PingEvent',
        'Detail': json.dumps({
            "message": "Ping!"
        }),
        'EventBusName': environ['EVENT_BUS_ARN']
    }
    event_bus.put_events(Entries=[event])

    logger.info("hello world!")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Pong",
        }),
    }
