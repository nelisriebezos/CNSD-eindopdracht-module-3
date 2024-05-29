import json
import logging
import boto3
from os import environ
from jose import jwt
from boto3.dynamodb.conditions import Key


logger = logging.getLogger()
logger.setLevel("INFO")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(environ["DYNAMODB_TABLE"])


def lambda_handler(event, context):
    user_id = jwt.get_unverified_claims(
        event["headers"]["Authorization"].replace("Bearer ", "")
    )["sub"]

    logger.info(event)

    oracle_id = event["pathParameters"]["instance_id"]

    response = table.query(
        IndexName="GSI-Collection-OracleId",
        KeyConditionExpression=Key("PK").eq(f"UserId#{user_id}")
        & Key("GSI2SK").begins_with(f"OracleId#{oracle_id}"),
    )

    if len(response["Items"]) == 0:
        return {"statusCode": 404}

    return {
        "statusCode": 200,
        "body": json.dumps(response["Items"]),
    }
