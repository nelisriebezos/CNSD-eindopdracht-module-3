import json
from jose import jwt
import os
from os import environ
from uuid import uuid4
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
    token_header: str = event["headers"]["Authorization"]

    if not token_header.startswith("Bearer "):
        raise Exception("Invalid authorization header")

    token_header = token_header[len("Bearer "):]

    claims = jwt.get_unverified_claims(token_header)

    return claims["sub"]

def lambda_handler(event, context):
    LOGGER.info("Starting create deck lambda")

    if not "body" in event or event["body"] == None:
        LOGGER.info("Missing body in request")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Missing 'name'",
            })
        }

    body = json.loads( event["body"] )

    if not "name" in body:
        LOGGER.info("Missing 'name' in request")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Missing 'name'",
            })
        }

    deck_name = body["name"]

    user_id = get_user_id(event)
    deck_id = str( uuid4() )

    LOGGER.info(f"Creating deck for user '{user_id}' with id '{deck_id}' and name '{deck_name}'")

    DECK_TABLE.put_item(Item={
        "PK": f"USER#{user_id}",
        "SK": f"DECK#{deck_id}",

        "data_type": "DECK",
        "user_id": user_id,
        "deck_id": deck_id,
        "deck_name": deck_name,
    })

    LOGGER.info("Successfully created new deck")

    return {
        "statusCode": 201,
        "body": json.dumps({
            "id": deck_id,
            "name": deck_name,
        }),
    }
