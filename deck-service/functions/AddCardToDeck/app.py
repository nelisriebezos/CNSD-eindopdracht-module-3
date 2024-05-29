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
from datetime import datetime

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

    if not "cardOracle" in body:
        LOGGER.info("Missing 'cardOracle' in request")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Missing 'cardOracle'",
            })
        }, None

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

def get_card(bearer_token: str, oracle_id: str, print_id: Optional[str] = None) -> Optional[dict]:
    url = f"{CARD_GATEWAY}/api/cards/{oracle_id}/{print_id}/" if print_id is not None else f"{CARD_GATEWAY}/api/cards/{oracle_id}/"

    LOGGER.info(f"Fetching card(s) from '{url}'")

    response = requests.get(url, headers={
        "Authorization": bearer_token,
    })

    if response.status_code == 404:
        LOGGER.info(f"Found no card with oracle id '{oracle_id}' (and instance id '{print_id}')")

        return None

    response_body = response.json()

    if response.status_code != 200:
        message = response_body["Message"]

        LOGGER.error(f"Error while fetching card from api: {response.status_code}\n {message}")

        return None

    if print_id is not None:
        LOGGER.info(f"Found card with oracle id '{oracle_id}' and instance id '{print_id}'")

        return response_body

    sorted_items = sorted(
        response_body["Items"],
        key=lambda item: datetime.strptime( item["ReleasedAt"], "%Y-%m-%d" ).timestamp(),
        reverse=True,
    )

    LOGGER.info(f"Found card with oracle id '{oracle_id}'")

    return next( iter(sorted_items), None )

def lambda_handler(event, context):
    LOGGER.info("Starting add card to deck lambda")

    error, body = parse_body(event)

    if error is not None:
        return error

    deck_card_id = str( uuid4() )
    user_id = get_user_id(event)
    deck_id = event["pathParameters"]["deck_id"]
    oracle_id = body["cardOracle"]
    card_location = body["cardLocation"]
    card_instance_id = body.get("cardInstanceId", None)
    card_print_id = body.get("cardPrintId", None)

    card = get_card(event["headers"]["Authorization"], oracle_id, card_print_id)

    if card is None:
        msg = f"Card with oracle with id '{oracle_id}' and with card print id '{card_print_id}' was not found" if card_instance_id is not None else f"Card with oracle with id '{oracle_id}' was not found"

        LOGGER.info(msg)

        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": msg,
            })
        }

    LOGGER.info("Removing disallowed keys from card response")

    for disallowed_key in DISALLOWED_DB_KEYS:
        if disallowed_key in card:
            del card[disallowed_key]

    if "CardFaces" in card:
        for card_face in card["CardFaces"]:
            for disallowed_key in DISALLOWED_DB_KEYS:
                if disallowed_key in card_face:
                    del card_face[disallowed_key]

    optional_card_instance_id_data = { "card_instance_id": card_instance_id } if card_instance_id is not None else {}

    LOGGER.info("Saving card to deck")

    DECK_TABLE.put_item(Item={
        "PK": f"USER#{user_id}#DECK#{deck_id}",
        "SK": f"DECK_CARD#{deck_card_id}",

        "data_type": "DECK_CARD",
        "user_id": user_id,
        "deck_id": deck_id,
        "deck_card_id": deck_card_id,
        "card_location": card_location,

        **optional_card_instance_id_data,

        **card,
    })

    LOGGER.info("Successfully saved card to deck")

    return {
        "statusCode": 201,
        "body": json.dumps({
            "deck_card_id": deck_card_id,
        }),
    }
