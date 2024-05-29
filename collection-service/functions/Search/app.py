import boto3
import logging
import json

from jose import jwt
from aws_xray_sdk.core import patch_all
from os import environ
from boto3.dynamodb.conditions import Key, Attr

if "DISABLE_XRAY" not in environ:
    patch_all()

logger = logging.getLogger()
logger.setLevel("INFO")

dynamodb = boto3.resource("dynamodb")
collection_table = dynamodb.Table(environ["DYNAMODB_TABLE"])


def lambda_handler(event, context):
    # Auth
    authorization_value = event.get("headers", {}).get("Authorization", None)
    if not authorization_value:
        logger.error("Invalid credentials")
        return {
            "headers": {
                "Content-Type": "application/json",
            },
            "statusCode": 401,
            "body": json.dumps({"Message": "JWT token not provided"}),
        }
    tmp_authorization_value = authorization_value.replace("Bearer ", "")
    cognito_username = jwt.get_unverified_claims(tmp_authorization_value).get("sub")
    logger.info(f"Cognito_username: {cognito_username}")

    # Optional params
    query_string_parameters = event.get("queryStringParameters", {}) or {}
    logger.info(f"{query_string_parameters = }")

    # Query param
    search_query = query_string_parameters.get("q", "").casefold()
    logger.info(f"Search input: {search_query}")

    # Pagination params
    last_evaluated_key = None
    pk_last_evaluated = query_string_parameters.get("pk-last-evaluated")
    sk_last_evaluated = query_string_parameters.get("sk-last-evaluated")
    logger.info(f"{pk_last_evaluated = }")
    logger.info(f"{sk_last_evaluated = }")
    if pk_last_evaluated is not None and sk_last_evaluated is not None:
        last_evaluated_key = {"PK": pk_last_evaluated, "SK": sk_last_evaluated}

    # Limiting param
    limit_value = 40
    user_defined_limit = query_string_parameters.get("limit")
    if user_defined_limit is not None:
        limit_value = int(user_defined_limit)

    # Construct query params
    db_query_params = {
        "KeyConditionExpression": Key("PK").eq(f"UserId#{cognito_username}"),
    }

    if search_query != "":
        db_query_params["FilterExpression"] = (
            Attr("LowerCaseOracleName").contains(search_query) |
            Attr("CombinedLowercaseOracleText").contains(search_query)
        )
    else:
        # If the user does a get all, all values will be retrieved
        db_query_params["Limit"] = limit_value

    if last_evaluated_key is not None:
        db_query_params["ExclusiveStartKey"] = last_evaluated_key

    logger.info(f"{db_query_params = }")

    items = []
    no_more_items_in_db = False

    # Keep searching until the required limit is reached or there are no more items
    while len(items) < limit_value:
        query_result = collection_table.query(**db_query_params)
        logger.info(f"{query_result = }")

        # Expand the items with the new results
        items = [*items, *query_result.get("Items", [])]

        if "LastEvaluatedKey" in query_result:
            db_query_params["ExclusiveStartKey"] = query_result["LastEvaluatedKey"]
        else:
            # Stop when there are no more items
            no_more_items_in_db = True
            break

    # Reduce the amount of items returned to the limit
    items = items[:limit_value]

    # Give pagination key when there are more items to be retrieved
    if not no_more_items_in_db:
        pk_last_evaluated = items[-1]["PK"]
        sk_last_evaluated = items[-1]["SK"]
    else:
        pk_last_evaluated = None
        sk_last_evaluated = None

    logger.info(f"All of the items returned: {items}")

    return {
        "headers": {
            "Content-Type": "application/json",
        },
        "statusCode": 200,
        "body": json.dumps(
            {
                "Items": items,
                "pk-last-evaluated": pk_last_evaluated,
                "sk-last-evaluated": sk_last_evaluated,
            }
        ),
    }
