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
        "queryStringParameters": {"q": "Oblivion"},
    }

    # Act
    result = lambda_handler(event, None)

    body = json.loads(result["Body"])

    # Assert
    assert body["Items"][0]["PK"] == "OracleId#517be4da-9aa0-4a83-a559-962df0450f2c"
    assert body["Items"][0]["SK"] == "PrintId#faf65512-8228-48f4-ba7b-d861b66d28c9"
    assert body["Items"][0]["OracleName"] == "Oblivion's Hunger"


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
        "queryStringParameters": {"q": "Creature"},
    }

    # Act
    result = lambda_handler(event, None)

    body = json.loads(result["Body"])

    # Assert
    assert body["Items"][0]["PK"] == "OracleId#517be4da-9aa0-4a83-a559-962df0450f2c"
    assert body["Items"][0]["SK"] == "PrintId#faf65512-8228-48f4-ba7b-d861b66d28c9"
    assert (
        body["Items"][0]["CombinedLowercaseOracleText"]
        == 'target creature you control gains indestructible until end of turn. draw a card if that creature has a +1/+1 counter on it. (damage and effects that say "destroy" don\'t destroy the creature.)'
    )


@patch.dict(
    os.environ,
    {
        "DYNAMODB_TABLE": DYNAMODB_TABLE_NAME,
        "DISABLE_XRAY": "True",
        "EVENT_BUS_ARN": "",
    },
)
def test_search_not_found(setup_dynamodb_collection):
    from functions.Search.app import lambda_handler

    # Arrange
    event = {
        "queryStringParameters": {"q": "Invalid"},
    }

    # Act
    result = lambda_handler(event, None)

    # Assert
    assert result["statusCode"] == 404


@patch.dict(
    os.environ,
    {
        "DYNAMODB_TABLE": DYNAMODB_TABLE_NAME,
        "DISABLE_XRAY": "True",
        "EVENT_BUS_ARN": "",
    },
)
def test_search_no_query(setup_dynamodb_collection):
    from functions.Search.app import lambda_handler

    # Arrange
    event = {}

    # Act
    result = lambda_handler(event, None)
    body = json.loads(result["Body"])

    # Assert
    assert result["statusCode"] == 406
    assert body["message"] == "query string parameter not provided"
