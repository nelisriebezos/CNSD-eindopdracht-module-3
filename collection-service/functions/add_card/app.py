import json
import os
import boto3
from botocore.exceptions import ClientError
from aws_xray_sdk.core import patch_all
import logging
from jose import jwt
import requests
import uuid
from os import environ

if "DISABLE_XRAY" not in environ:
    patch_all()

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")

DYNAMO_DB = boto3.resource("dynamodb", region_name="us-east-1")
DYNAMO_DB_COLLECTION_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
COLLECTION_TABLE = DYNAMO_DB.Table(DYNAMO_DB_COLLECTION_TABLE_NAME)
STAGE = os.getenv("STAGE")
ssm = boto3.client("ssm")


def fetch_api_url():
    LOGGER.info("Fetching api url from ssm")
    try:
        parameter = ssm.get_parameter(Name=f'/{STAGE}/MTGCardApi/url')
        LOGGER.info(f"Fetched api url: {parameter['Parameter']['Value']}")
        return parameter['Parameter']['Value']
    except ClientError as e:
        LOGGER.error(f"Error while fetching api url from ssm: {e}")
        raise e


def parse_card_item(item, user_id, condition, deck_id):
    card_instance_id = str(uuid.uuid4())
    face_items = []

    for face in item["CardFaces"]:
        face_items.append(
            {
                "OracleText": face["OracleText"],
                "ManaCost": face["ManaCost"],
                "TypeLine": face["TypeLine"],
                "FaceName": face["FaceName"],
                "FlavorText": face["FlavorText"],
                "ImageUrl": face["ImageUrl"],
                "Colors": face["Colors"],
                "LowercaseFaceName": face["LowercaseFaceName"],
                "LowercaseOracleText": face["LowercaseOracleText"],
            }
        )

    tmp = {
        "PK": f"UserId#{user_id}",
        "SK": f"CardInstanceId#{card_instance_id}",
        "PrintId": item["PrintId"],
        "OracleId": item["OracleId"],
        "CardInstanceId": card_instance_id,
        "Condition": condition,
        "OracleName": item["OracleName"],
        "SetName": item["SetName"],
        "ReleasedAt": item["ReleasedAt"],
        "Rarity": item["Rarity"],
        "Price": item["Price"],
        "LowerCaseOracleName": item["LowerCaseOracleName"],
        "CardFaces": face_items,
        "GSI2SK": f"OracleId#{item['OracleId']}#CardInstanceId#{card_instance_id}",
    }

    if deck_id:
        tmp["DeckId"] = deck_id
        tmp["GSI1SK"] = f"DeckId#{item['DeckId']}#CardInstanceId#{card_instance_id}"

    return tmp


def save_card_to_db(item, user_id, condition, deck_id):
    try:
        card_instance_item = parse_card_item(item, user_id, condition, deck_id)
        LOGGER.info(f"Saving card instance: {card_instance_item}")
        COLLECTION_TABLE.put_item(Item=card_instance_item)
        return card_instance_item
    except ClientError as e:
        LOGGER.error(f"Error while saving card instances to the database: {e}")
        raise e


def get_user_id(event: dict) -> str:
    token_header: str = event["headers"]["Authorization"].replace("Bearer ", "")
    return jwt.get_unverified_claims(token_header)["sub"]


def lambda_handler(event, context):
    LOGGER.info("Starting add card to collection lambda")
    LOGGER.info(f"Event body: {event['body'] }")

    body = json.loads(event["body"])
    oracle_id = body["oracle_id"]
    print_id = body["print_id"]
    condition = body["condition"]
    deck_id = body.get("deck_id", "")
    user_id = get_user_id(event)

    try:
        api_url = fetch_api_url()

        LOGGER.info(f"Fetching card from api: {api_url}/api/cards/{oracle_id}/{print_id}")

        api_response = requests.get(
            f"{api_url}/api/cards/{oracle_id}/{print_id}",
            headers={"Authorization": event["headers"]["Authorization"]},
        )

        LOGGER.info(f"{api_response = }")

        api_response_code = api_response.status_code
        api_response_body = api_response.json()

        if api_response_code != 200:
            LOGGER.info(f"{api_response_code = }")
            LOGGER.info(f"{api_response_body = }")
            api_error_message = api_response_body["Message"]
            LOGGER.error(
                f"Error while fetching card from api: {api_response_code}\n {api_error_message}"
            )
            return {
                "statusCode": api_response_code,
                "body": json.dumps({"Message": api_error_message}),
            }

        saved_card = save_card_to_db(api_response_body, user_id, condition, deck_id)

        LOGGER.info(
            f"Successfully added the following card to the collection: {saved_card}"
        )

        return {"statusCode": 201, "body": json.dumps(saved_card)}
    except ClientError as e:
        LOGGER.error(f"Error while saving the card: {e}")
        return {"statusCode": 500, "body": json.dumps({"Message": e.response})}
