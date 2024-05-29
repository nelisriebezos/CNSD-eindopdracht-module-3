import json
import os
from unittest.mock import patch
from .jwt_generator import generate_test_jwt
from .conftest import DYNAMODB_TABLE_NAME


@patch.dict(os.environ, {"DYNAMO_DB_DECK_TABLE_NAME": DYNAMODB_TABLE_NAME, "DISABLE_XRAY": "True"})
def test_get_deck_card_by_id(setup_dynamodb_collection):
    from functions.GetCardByIdFromDeck.app import lambda_handler

    # Insert mock data into the table
    table = setup_dynamodb_collection
    table.put_item(Item={
        "PK": "USER#test-user",
        "SK": "DECK#1",
        "data_type": "DECK",
        "user_id": "test-user",
        "deck_id": "1",
        "deck_name": "Test deck",
    })
    table.put_item(Item={
        "PK": "USER#test-user#DECK#1",
        "SK": "DECK_CARD#1",
        "data_type": "DECK_CARD",
        "user_id": "test-user",
        "deck_id": "1",
        "deck_card_id": "1",
        "OracleName": "Swords of Plowshares",
    })

    # Mock API Gateway event
    event = {
        'pathParameters': {'deck_id': '1', 'card_id': '1'},
        'headers': {'Authorization': f'Bearer {generate_test_jwt()}'}
    }

    # Invoke the lambda handler
    response = lambda_handler(event, {})

    # Assert the response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['data_type'] == 'DECK_CARD'
    assert body['user_id'] == 'test-user'
    assert body['deck_id'] == '1'
    assert body['deck_card_id'] == '1'
    assert body['OracleName'] == 'Swords of Plowshares'


@patch.dict(os.environ, {"DYNAMO_DB_DECK_TABLE_NAME": DYNAMODB_TABLE_NAME, "DISABLE_XRAY": "True"})
def test_get_deck_card_by_id_card_not_found(setup_dynamodb_collection):
    from functions.GetCardByIdFromDeck.app import lambda_handler

    # Insert mock data into the table
    table = setup_dynamodb_collection
    table.put_item(Item={
        "PK": "USER#test-user",
        "SK": "DECK#1",
        "data_type": "DECK",
        "user_id": "test-user",
        "deck_id": "1",
        "deck_name": "Test deck",
    })
    table.put_item(Item={
        "PK": "USER#test-user#DECK#1",
        "SK": "DECK_CARD#1",
        "data_type": "DECK_CARD",
        "user_id": "test-user",
        "deck_id": "1",
        "deck_card_id": "1",
        "OracleName": "Swords of Plowshares",
    })

    # Mock API Gateway event
    event = {
        'pathParameters': {'deck_id': '1', 'card_id': '2'},
        'headers': {'Authorization': f'Bearer {generate_test_jwt()}'}
    }

    # Invoke the lambda handler
    response = lambda_handler(event, {})

    # Assert the response
    assert response['statusCode'] == 404


@patch.dict(os.environ, {"DYNAMO_DB_DECK_TABLE_NAME": DYNAMODB_TABLE_NAME, "DISABLE_XRAY": "True"})
def test_get_deck_card_by_id_deck_not_found(setup_dynamodb_collection):
    from functions.GetCardByIdFromDeck.app import lambda_handler

    # Insert mock data into the table
    table = setup_dynamodb_collection
    table.put_item(Item={
        "PK": "USER#test-user",
        "SK": "DECK#1",
        "data_type": "DECK",
        "user_id": "test-user",
        "deck_id": "1",
        "deck_name": "Test deck",
    })
    table.put_item(Item={
        "PK": "USER#test-user#DECK#1",
        "SK": "DECK_CARD#1",
        "data_type": "DECK_CARD",
        "user_id": "test-user",
        "deck_id": "1",
        "deck_card_id": "1",
        "OracleId": "Swords of Plowshares",
    })

    # Mock API Gateway event
    event = {
        'pathParameters': {'deck_id': '2', 'card_id': '1'},
        'headers': {'Authorization': f'Bearer {generate_test_jwt()}'}
    }

    # Invoke the lambda handler
    response = lambda_handler(event, {})

    # Assert the response
    assert response['statusCode'] == 404
