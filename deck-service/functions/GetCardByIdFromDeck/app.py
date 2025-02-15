import json
from jose import jwt
import os
from os import environ
import boto3
from aws_xray_sdk.core import patch_all
import logging

if 'DISABLE_XRAY' not in environ:
    patch_all()

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")

DYNAMO_DB = boto3.resource("dynamodb")
DYNAMO_DB_DECK_TABLE_NAME = os.getenv("DYNAMO_DB_DECK_TABLE_NAME")
DECK_TABLE = DYNAMO_DB.Table(DYNAMO_DB_DECK_TABLE_NAME)

def get_user_id(event: dict) -> str:
    token_header: str = event["headers"]["Authorization"].replace("Bearer ", "")
    claims = jwt.get_unverified_claims(token_header)
    return claims["sub"]

def lambda_handler(event, context):
    LOGGER.info("Starting get card by id from deck lambda")

    user_id = get_user_id(event)
    deck_id = event["pathParameters"]["deck_id"]
    card_id = event["pathParameters"]["card_id"]

    LOGGER.info(f"Getting deckcards for deck with id '{deck_id}'")

    db_response = DECK_TABLE.get_item(Key={
        "PK": f"USER#{user_id}#DECK#{deck_id}",
        "SK": f"DECK_CARD#{card_id}"
    })

    LOGGER.info(f"{db_response = }")

    if 'Item' not in db_response:
        return {
            "statusCode": 404,
        }

    return {
        "statusCode": 200,
        "body": json.dumps(db_response["Item"]),
    }
