import json
import os
from unittest.mock import patch
from .jwt_generator import generate_test_jwt


@patch.dict(os.environ, {"DYNAMODB_TABLE": "test-table", "DISABLE_XRAY": "True"})
def test_get_card_instance_by_id(setup_dynamodb_collection):
    from functions.get_instance.app import lambda_handler

    # Insert mock data into the table
    table = setup_dynamodb_collection
    table.put_item(
        Item={
            "PK": "UserId#test-user",
            "SK": "CardInstanceId#1#Card",
            "CardInstanceId": "1",
            "DataType": "Card",
            "DeckId": "1",
            "OracleId": "d6329dcc-b450-482a-8ee3-45449f7a4b3d",
            "GSI1SK": "DeckId#1",
            "GSI2SK": "OracleId#d6329dcc-b450-482a-8ee3-45449f7a4b3d#CardInstanceId#1",
        }
    )
    table.put_item(
        Item={
            "PK": "UserId#test-user",
            "SK": "CardInstanceId#2#Card",
            "CardInstanceId": "2",
            "OracleId": "d6329dcc-b450-482a-8ee3-45449f7a4b3d",
            "DataType": "Card",
            "GSI2SK": "OracleId#d6329dcc-b450-482a-8ee3-45449f7a4b3d#CardInstanceId#2",
        }
    )

    # Mock API Gateway event
    event = {
        "pathParameters": {"instance_id": "d6329dcc-b450-482a-8ee3-45449f7a4b3d"},
        "headers": {"Authorization": f"Bearer {generate_test_jwt()}"},
    }

    # Invoke the lambda handler
    response = lambda_handler(event, {})

    # Assert the response
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    print(body)

    instance_one = body[0]
    instance_two = body[1]

    assert instance_one["CardInstanceId"] == "1"
    assert instance_one["DataType"] == "Card"
    assert instance_one["DeckId"] == "1"

    assert instance_two["CardInstanceId"] == "2"
    assert instance_two["DataType"] == "Card"


@patch.dict(os.environ, {"DYNAMODB_TABLE": "test-table", "DISABLE_XRAY": "True"})
def test_get_card_instance_by_id_not_found(setup_dynamodb_collection):
    from functions.get_instance.app import lambda_handler

    # Insert mock data into the table
    table = setup_dynamodb_collection
    table.put_item(
        Item={
            "PK": "UserId#test-user",
            "SK": "CardInstanceId#1#Card",
            "CardInstanceId": "1",
            "DataType": "Card",
            "DeckId": "1",
            "OracleId": "d6329dcc-b450-482a-8ee3-45449f7a4b3d",
            "GSI1SK": "DeckId#1",
            "GSI2SK": "OracleId#d6329dcc-b450-482a-8ee3-45449f7a4b3d#CardInstanceId#1",
        }
    )
    table.put_item(
        Item={
            "PK": "UserId#test-user",
            "SK": "CardInstanceId#2#Card",
            "CardInstanceId": "2",
            "OracleId": "d6329dcc-b450-482a-8ee3-45449f7a4b3d",
            "DataType": "Card",
            "GSI2SK": "OracleId#d6329dcc-b450-482a-8ee3-45449f7a4b3d#CardInstanceId#2",
        }
    )

    # Mock API Gateway event
    event = {
        "pathParameters": {"instance_id": "wrongdcc-b450-482a-8ee3-45449f7a4b3d"},
        "headers": {"Authorization": f"Bearer {generate_test_jwt()}"},
    }

    # Invoke the lambda handler
    response = lambda_handler(event, {})

    # Assert the response
    assert response["statusCode"] == 404
