import json
from jose import jwt
import os
from os import environ
from uuid import uuid4
import boto3
from aws_xray_sdk.core import patch_all
import logging
from typing import Optional, Tuple
import requests

if 'DISABLE_XRAY' not in environ:
    patch_all()

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")

AVAILABLE_DECK_LOCATIONS = [ "COMMANDER", "MAIN_DECK", "SIDE_DECK" ]
DISALLOWED_DB_KEYS = [
    "PK",
    "SK",

    "data_type",
    "user_id",
    "deck_id",
    "deck_card_id",
    "card_location",
    "card_instance_id",

    "CombinedLowercaseOracleText",
    "LowerCaseOracleName",
    "LowercaseOracleText",
    "LowercaseFaceName",
]

STAGE = os.getenv("STAGE")
SSM = boto3.client("ssm")

CARD_GATEWAY = SSM.get_parameter(Name=f"/{STAGE}/MTGCardApi/url")["Parameter"]["Value"]

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

def parse_body(unparsed_body: str) -> Tuple[Optional[dict], Optional[dict]]:
    LOGGER.info("Parsing request body")

    if not "body" in unparsed_body or unparsed_body["body"] == None:
        LOGGER.info("Missing body in request")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Missing body in request",
            })
        }, None

    body = json.loads( unparsed_body["body"] )

    if "cardInstanceId" in body and "cardPrintId" not in body:
        LOGGER.info("'cardPrintId' should be set when 'cardInstanceId' is set")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "'cardPrintId' should be set when 'cardInstanceId' is set",
            })
        }, None

    if not "cardLocation" in body:
        LOGGER.info("Missing 'cardLocation' in request")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Missing 'cardLocation'",
            })
        }, None

    cardLocation = body["cardLocation"]

    if cardLocation not in AVAILABLE_DECK_LOCATIONS:
        LOGGER.info(f"Invalid deck location: '{cardLocation}'")

        allowed_locations = ", ".join(AVAILABLE_DECK_LOCATIONS)

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"Invalid deck location: '{cardLocation}'. Expected one of: '{allowed_locations}'",
            })
        }, None

    LOGGER.info("Successfully parsed request body")

    return None, body

def get_card(bearer_token: str, oracle_id: str, print_id: str) -> Optional[dict]:
    url = f"{CARD_GATEWAY}/api/cards/{oracle_id}/{print_id}/"

    LOGGER.info(f"Fetching card from '{url}'")

    response = requests.get(url, headers={
        "Authorization": bearer_token,
    })

    print(url)
    print(response, response.status_code, response.content)

    if response.status_code == 404:
        LOGGER.info(f"Found no card with oracle id '{oracle_id}' (and instance id '{print_id}')")

        return None

    response_body = response.json()

    if response.status_code != 200:
        message = response_body["Message"]

        LOGGER.error(f"Error while fetching card from api: {response.status_code}\n {message}")

        return None

    LOGGER.info(f"Found card with oracle id '{oracle_id}' and instance id '{print_id}'")

    return response_body

def update_card(bearer_token: str, user_id: str, deck_id: str, deck_card_id: str, oracle_id: str, card_print_id: str, card_instance_id: Optional[str]) -> Optional[str]:
    if card_instance_id is None:
        LOGGER.info(f"Removing card instance from deck '{deck_id}' from user '{user_id}', card '{deck_card_id}'")

        DECK_TABLE.update_item(
            Key={ "PK": f"USER#{user_id}#DECK#{deck_id}", "SK": f"DECK_CARD#{deck_card_id}" },
            UpdateExpression="REMOVE #card_instance_id",
            ExpressionAttributeNames={ "#card_instance_id": "card_instance_id" },
        )

        return None

    card = get_card(bearer_token, oracle_id, card_print_id)

    if card is None:
        return f"No card with oracle '{oracle_id}' and print '{card_print_id}' found"

    for disallowed_key in DISALLOWED_DB_KEYS:
        if disallowed_key in card:
            del card[disallowed_key]

    if "CardFaces" in card:
        for card_face in card["CardFaces"]:
            for disallowed_key in DISALLOWED_DB_KEYS:
                if disallowed_key in card_face:
                    del card_face[disallowed_key]

    query = []
    attribute_names = {}
    attribute_values = {}

    for key in card.keys():
        query.append(f"#{key} = :{key}")
        attribute_names[f"#{key}"] = key
        attribute_values[f":{key}"] = card[key]

    query.append(f"#card_instance_id = :card_instance_id")
    attribute_names["#card_instance_id"] = "card_instance_id"
    attribute_values[":card_instance_id"] = card_instance_id

    LOGGER.info(f"Updating card instance from deck '{deck_id}' from user '{user_id}', card '{deck_card_id}' with new card information")

    DECK_TABLE.update_item(
        Key={ "PK": f"USER#{user_id}#DECK#{deck_id}", "SK": f"DECK_CARD#{deck_card_id}" },
        UpdateExpression="SET " + ", ".join(query),
        ExpressionAttributeNames=attribute_names,
        ExpressionAttributeValues=attribute_values,
    )

    return None

def lambda_handler(event, context):
    LOGGER.info("Starting edit deck card lambda")

    error, body = parse_body(event)

    if error is not None:
        return error

    user_id = get_user_id(event)
    deck_id = event["pathParameters"]["deck_id"]
    deck_card_id = event["pathParameters"]["card_id"]
    card_location = body["cardLocation"]
    card_instance_id = body.get("cardInstanceId", None)
    card_print_id = body.get("cardPrintId", None)

    LOGGER.info(f"Updating deck card location for user '{user_id}' with deck id '{deck_id}' and card id '{deck_card_id}'")

    db_item = DECK_TABLE.update_item(
        Key={ "PK": f"USER#{user_id}#DECK#{deck_id}", "SK": f"DECK_CARD#{deck_card_id}" },
        UpdateExpression="SET #card_location = :card_location",
        ExpressionAttributeNames={ "#card_location": "card_location" },
        ExpressionAttributeValues={ ":card_location": card_location },
        ReturnValues="ALL_NEW",
    )["Attributes"]

    if db_item["PrintId"] != card_print_id:
        error = update_card(event["headers"]["Authorization"], user_id, deck_id, deck_card_id, db_item["OracleId"], card_print_id, card_instance_id)

        print(error)

        if error is not None:
            LOGGER.error(f"Error occurred while updating card: {error}")

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": error,
                }),
            }

    LOGGER.info("Successfully updated deck card")

    return {
        "statusCode": 204,
        "body": json.dumps(None),
    }
