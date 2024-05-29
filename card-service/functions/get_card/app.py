import json
import logging
import boto3
from os import environ
from aws_xray_sdk.core import patch_all
from botocore.exceptions import ClientError

if 'DISABLE_XRAY' not in environ:
    patch_all()

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(environ['DYNAMODB_TABLE_NAME'])


def lambda_handler(event, context):
    LOGGER.info("Starting get card from database lambda")

    card_oracle_id = event["pathParameters"]["oracle_id"]
    card_print_id = event["pathParameters"]["print_id"]

    try:
        response = table.get_item(Key={
            'PK': f'OracleId#{card_oracle_id}',
            'SK': f'PrintId#{card_print_id}'
        })

        if "Item" not in response:
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

    item = response["Item"]
    item.pop('RemoveAt', None)

    LOGGER.info(f'items to be returned: {item}')

    return {
        "statusCode": 200,
        "body": json.dumps(item)
    }
