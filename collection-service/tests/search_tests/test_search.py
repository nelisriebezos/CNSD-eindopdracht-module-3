import os
import json
import logging
from unittest.mock import patch
from .jwt_generator import generate_test_jwt
from .conftest import DYNAMODB_TABLE_NAME

COGINTO_USERNAME = "test@example.com"
COGINTO_PASSWORD = "NewPassword456!"

logger = logging.getLogger()
logger.setLevel("INFO")


@patch.dict(
    os.environ,
    {
        "DYNAMODB_TABLE": DYNAMODB_TABLE_NAME,
        "DISABLE_XRAY": "True",
        "EVENT_BUS_ARN": "",
    },
)
def test_search_oraclename(setup_dynamodb_collection_with_items):
    from functions.Search.app import lambda_handler

    event = {
        "headers": {"Authorization": f"Bearer {generate_test_jwt()}"},
        # "queryStringParameters": {"q": "Beloved"},
    }

    # Act
    result = lambda_handler(event, None)

    body = json.loads(result["body"])

    # Assert
    assert len(body["Items"]) == 1
    assert body["Items"][0]["PK"] == "UserId#test-user"
    assert body["Items"][0]["SK"] == "CardInstanceId#1"
    assert body["Items"][0]["OracleName"] == "Beloved Beggar // Generous Soul"


@patch.dict(
    os.environ,
    {
        "DYNAMODB_TABLE": DYNAMODB_TABLE_NAME,
        "DISABLE_XRAY": "True",
        "EVENT_BUS_ARN": "",
    },
)
def test_search_oracletext(setup_dynamodb_collection_with_items):
    from functions.Search.app import lambda_handler

    event = {
        "headers": {"Authorization": f"Bearer {generate_test_jwt()}"},
        "queryStringParameters": {"q": "Graveyard"},
    }

    # Act
    result = lambda_handler(event, None)

    body = json.loads(result["body"])

    # Assert
    assert body["Items"][0]["PK"] == "UserId#test-user"
    assert body["Items"][0]["SK"] == "CardInstanceId#1"
    assert body["Items"][0]["OracleName"] == "Beloved Beggar // Generous Soul"


@patch.dict(
    os.environ,
    {
        "DYNAMODB_TABLE": DYNAMODB_TABLE_NAME,
        "DISABLE_XRAY": "True",
        "EVENT_BUS_ARN": "",
    },
)
def test_search_no_authorization(setup_dynamodb_collection):
    from functions.Search.app import lambda_handler

    # Arrange
    event = {
        "queryStringParameters": {"q": "Invalid"},
    }

    # Act
    result = lambda_handler(event, None)
    body = json.loads(result["body"])

    # Assert
    assert result["statusCode"] == 401
    assert body["Message"] == "JWT token not provided"


def test_search_no_query(setup_dynamodb_collection_with_multiple_items):
    from functions.Search.app import lambda_handler

    # Arrange
    event = {
        "headers": {"Authorization": generate_test_jwt()},
    }

    # Act
    result = lambda_handler(event, None)
    body = json.loads(result["body"])

    # Assert
    assert body["Items"][0]["PK"] == "UserId#test-user"
    assert body["Items"][0]["SK"] == "CardInstanceId#1"
    assert body["Items"][0]["OracleName"] == "Beloved Beggar // Generous Soul"

    assert body["Items"][1]["PK"] == "UserId#test-user"
    assert (
        body["Items"][1]["SK"] == "CardInstanceId#ed1387cd-0ff9-41fc-825c-1b1cdb6a52e1"
    )
    assert body["Items"][1]["OracleName"] == "Chicken Egg"


def test_search_limit_2(setup_dynamodb_collection_with_three_items):
    from functions.Search.app import lambda_handler

    # Arrange
    event = {
        "headers": {"Authorization": generate_test_jwt()},
        "queryStringParameters": {"limit": 2},
    }

    # Act
    result = lambda_handler(event, None)
    body = json.loads(result["body"])

    items_length = len(body["Items"])

    # Assert
    assert items_length == 2


def test_search_limit_2_start_at_second(setup_dynamodb_collection_with_three_items):
    from functions.Search.app import lambda_handler

    # Arrange
    event = {
        "headers": {"Authorization": generate_test_jwt()},
        "queryStringParameters": {
            "limit": 2,
            "pk-last-evaluated": "UserId#test-user",
            "sk-last-evaluated": "CardInstanceId#1",
        },
    }

    # Act
    result = lambda_handler(event, None)
    body = json.loads(result["body"])

    items_length = len(body["Items"])

    # Assert
    assert items_length == 2

    # Items in a dynamodb database are sorted in lexicographical order so numbers first
    assert body["Items"][0]["PK"] == "UserId#test-user"
    assert (
        body["Items"][0]["SK"] == "CardInstanceId#691387cd-0ff9-41fc-825c-1b1cdb6a52e1"
    )
    assert body["Items"][0]["OracleName"] == "69 Chicken Egg"

    assert body["Items"][1]["PK"] == "UserId#test-user"
    assert (
        body["Items"][1]["SK"] == "CardInstanceId#ed1387cd-0ff9-41fc-825c-1b1cdb6a52e1"
    )
    assert body["Items"][1]["OracleName"] == "Chicken Egg"
