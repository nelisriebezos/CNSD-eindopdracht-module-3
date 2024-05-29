import os
import boto3
from aws_xray_sdk.core import patch_all
import logging
from jose import jwt
from boto3.dynamodb.conditions import Key
from os import environ
import json

if 'DISABLE_XRAY' not in environ:
    patch_all()

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")

DYNAMO_DB = boto3.resource("dynamodb", region_name="us-east-1")
DYNAMO_DB_COLLECTION_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
table = DYNAMO_DB.Table(DYNAMO_DB_COLLECTION_TABLE_NAME)

def lambda_handler(event, context):
    LOGGER.info(f"Deleting card with id: {event['pathParameters']['card_id']}")
    user_id = jwt.get_unverified_claims(event['headers']['Authorization'].replace("Bearer ", ""))["sub"]
    deck_id = event["pathParameters"]["deck_id"]
    card_id = event["pathParameters"]["card_id"]

    PK = f'USER#{user_id}#DECK#{deck_id}'
    SK = f'DECK_CARD#{card_id}'

    get_response = table.query(
        KeyConditionExpression=Key('PK').eq(PK) &
                               Key('SK').eq(SK),
    )

    if len(get_response['Items']) == 0:
        LOGGER.info(f"Deck card with id: {event['pathParameters']['card_id']} not found")
        return {
            "statusCode": 404
        }

    delete_response = table.delete_item(
        Key={
            'PK': PK,
            'SK': SK
        }
    )

    if delete_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        LOGGER.info(f"Error while removing card with id: {card_id}")
        return {
            "statusCode": 500
        }
    else:
        LOGGER.info(f"Deck card with id: {card_id} has been deleted")
        return {
            "statusCode": 200,
            "body": "Card has been removed from deck",
        }

