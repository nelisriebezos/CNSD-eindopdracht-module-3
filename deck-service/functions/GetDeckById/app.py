import json
from jose import jwt
import os
from os import environ
import boto3
from boto3.dynamodb.conditions import Key
from aws_xray_sdk.core import patch_all
import logging

if 'DISABLE_XRAY' not in environ:
    patch_all()

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")

DYNAMO_DB = boto3.resource("dynamodb")
DYNAMO_DB_DECK_TABLE_NAME = os.getenv("DYNAMO_DB_DECK_TABLE_NAME")
DECK_TABLE = DYNAMO_DB.Table(DYNAMO_DB_DECK_TABLE_NAME)

def parse_deck(db_data: dict) -> dict:
    return {
        "id": db_data["deck_id"],
        "name": db_data["deck_name"],
    }

def get_user_id(event: dict) -> str:
    token_header: str = event["headers"]["Authorization"].replace("Bearer ", "")
    claims = jwt.get_unverified_claims(token_header)
    return claims["sub"]

def lambda_handler(event, context):
    LOGGER.info("Starting get deck lambda")

    user_id = get_user_id(event)

    LOGGER.info(f"Getting decks for user with id '{user_id}'")

    db_items = DECK_TABLE.query(
        KeyConditionExpression=Key("PK").eq(f"USER#{user_id}") & Key("SK").eq(f"DECK#{event['pathParameters']['deck_id']}"),
        ProjectionExpression="deck_id, deck_name",
    )

    if len(db_items["Items"]) == 0:
        return {
            "statusCode": 404,
        }

    return {
        "statusCode": 200,
        "body": json.dumps(parse_deck(db_items["Items"][0])),
    }
