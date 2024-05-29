import boto3
import logging
import json

from jose import jwt
from aws_xray_sdk.core import patch_all
from os import environ
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

if "DISABLE_XRAY" not in environ:
    patch_all()

logger = logging.getLogger()
logger.setLevel("INFO")

dynamodb = boto3.resource("dynamodb")
collection_table = dynamodb.Table(environ["DYNAMODB_TABLE"])


def lambda_handler(event, context):
    query_string_parameters = event.get("queryStringParameters", {})

    search_value = (
        query_string_parameters.get("q")
        if query_string_parameters is not None
        else None
    )

    logger.info(f"Search input: {search_value}")

    if not search_value:
        return {
            "headers": {
                "Content-Type": "application/json",
            },
            "statusCode": 406,
            "Body": json.dumps({"message": "query string parameter not provided"}),
        }

    # Search query

    search_query = search_value
    search_query = search_query.casefold()
    logger.info(f"Search_query: {search_query}")

    result = search_for_querystring(
        table=collection_table,
        search_query=search_query,
    )

    logger.info(f"Query success: {result}")
    items = result["Items"]
    logger.info(f"All of the items returned: {items}")

    if not items:
        logger.info("No items found")
        return {
            "headers": {
                "Content-Type": "application/json",
            },
            "statusCode": 404,
            "Body": json.dumps({"message": "Not found"}),
        }

    return {
        "headers": {
            "Content-Type": "application/json",
        },
        "statusCode": 200,
        "Body": json.dumps({"Items": items}),
    }


def search_for_querystring(table, search_query):
    try:
        return table.scan(
            FilterExpression=Attr("LowerCaseOracleName").contains(search_query)
            | Attr("CombinedLowercaseOracleText").contains(search_query)
            | Attr("LowerCaseOracleName").contains(search_query)
            & Attr("CombinedLowercaseOracleText").contains(search_query),
        )
    except ClientError as e:
        logger.error(f"ClientError occured while scanning, { e }")
        raise
    except:
        logger.error(f"Error occured while scanning, { e }")
        raise
