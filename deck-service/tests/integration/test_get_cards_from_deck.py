import json
import os
from unittest.mock import patch
from .jwt_generator import generate_test_jwt
from .conftest import DYNAMODB_TABLE_NAME


@patch.dict(os.environ, {"DYNAMO_DB_DECK_TABLE_NAME": DYNAMODB_TABLE_NAME, "DISABLE_XRAY": "True"})
def test_get_collection(setup_dynamodb_collection):
    from functions.GetCardsFromDeck.app import lambda_handler

    # Insert mock data into the table
    table = setup_dynamodb_collection
    table.put_item(Item={
        "PK": "USER#test-user",
        "SK": "DECK#1",
        "DataType": "DECK",
        "UserId": "test-user",
        "DeckId": "1",
        "DeckName": "Test deck",
    })
    table.put_item(Item={
        "PK": "USER#test-user#DECK#1",
        "SK": "DECK_CARD#1",
        "DataType": "DECK_CARD",
        "UserId": "test-user",
        "DeckId": "1",
        "DeckCardId": "1",
        "CardName": "Swords of Plowshares",
    })
    table.put_item(Item={
        "PK": "USER#test-user#DECK#1",
        "SK": "DECK_CARD#2",
        "DataType": "DECK_CARD",
        "UserId": "test-user",
        "DeckId": "1",
        "DeckCardId": "2",
        "CardName": "Swords of Plowshares",
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
    assert len(body) == 2
    item_1 = body[0]
    assert item_1['DataType'] == 'DECK_CARD'
    assert item_1['UserId'] == 'test-user'
    assert item_1['DeckId'] == '1'
    assert item_1['DeckCardId'] == '1'
    assert item_1['CardName'] == 'Swords of Plowshares'
