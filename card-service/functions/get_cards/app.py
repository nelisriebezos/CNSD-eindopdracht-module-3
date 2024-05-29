import json
import logging
import boto3
from os import environ
from aws_xray_sdk.core import patch_all
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

if 'DISABLE_XRAY' not in environ:
    patch_all()

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(environ['DYNAMODB_TABLE_NAME'])


def lambda_handler(event, context):
    oracleId = event["pathParameters"]["oracle_id"]

    try:
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f"OracleId#{oracleId}"),
        )
        items = response["Items"]

        if len(items) == 0:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "Message": "Card not found."
                })
            }

    except ClientError as e:
        LOGGER.error(f"Error while fetching card: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"Message": "Server error while fetching card."})
        }

    LOGGER.info(f'items to be returned: {items}')

    for item in items:
        item.pop('RemoveAt', None)

    return {
        "statusCode": 200,
        "body": json.dumps({"Items": items})
    }
