import os
import boto3
from boto3.dynamodb.conditions import Key
from unittest.mock import patch
from moto import mock_dynamodb
import logging
import importlib
import pytest
import time
from jose import jwt

logger = logging.getLogger()
logger.setLevel("INFO")

user_id = "1"
deck_id = "1"
card_id = "1"
card_location = "1"
card_instance_id = "6c538e3f-068d-44af-9117-ef3f653831d2"
table_name = "test-deck-table"

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto. Otherwise it will deploy it for real"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def setup_table():
    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"},
                              {"AttributeName": "SK", "AttributeType": "S"}],
        BillingMode='PAY_PER_REQUEST'
    )
    return table

def generate_jwt_token(user_id: str = "test-user", secret_key: str = "secret", algorithm: str = "HS256",
                       claims: dict = {}) -> str:
    default_claims = {
        'iss': 'test_issuer',
        'sub': user_id,
        'aud': 'test_audience',
        'exp': int(time.time()) + 3600,
        'iat': int(time.time()),
        'cognito:username': user_id
    }

    all_claims = {**default_claims, **claims}
    token = jwt.encode(all_claims, secret_key, algorithm=algorithm)
    return token


def get_deck_with_card():
    return {
        "PK": f"USER#{user_id}#DECK#{deck_id}",
        "SK": f"DECK_CARD#{card_id}",

        "data_type": "DECK_CARD",
        "user_id": user_id,
        "deck_id": deck_id,
        "card_id": card_id,
        "card_location": card_location,
        "card_instance_id": card_instance_id,
    }

@patch.dict(os.environ, {"DISABLE_XRAY": "True",
                         "DYNAMODB_TABLE_NAME": table_name})
@mock_dynamodb
def test_remove_card_successfull(aws_credentials):
    # Arrange
    table = setup_table()

    event = {
        "pathParameters": {
            "user_id": "1",
            "deck_id": "1",
            "card_id": "1"
        },
        "headers": {
            "Authorization": f"Bearer {generate_jwt_token(user_id=user_id)}"
        }
    }

    put_response = table.put_item(Item=get_deck_with_card())

    response = table.query(
        KeyConditionExpression=Key('PK').eq(f"USER#{user_id}#DECK#{deck_id}") &
                               Key('SK').eq(f"DECK_CARD#{card_id}")
    )

    assert len(response['Items']) == 1

    # Act
    import functions.RemoveCard.app
    importlib.reload(functions.RemoveCard.app)
    functions.RemoveCard.app.lambda_handler(event, {})

    # Assert
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f"USER#{user_id}#DECK#{deck_id}") &
                               Key('SK').eq(f"DECK_CARD#{card_id}")
    )

    assert put_response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert len(response['Items']) == 0



@patch.dict(os.environ, {"DISABLE_XRAY": "True",
                         "DYNAMODB_TABLE_NAME": table_name})
@mock_dynamodb
def test_remove_non_existent_card(aws_credentials):
    # Arrange
    table = setup_table()

    event = {
        "pathParameters": {
            "user_id": "1",
            "deck_id": "1",
            "card_id": "1"
        },
        "headers": {
            "Authorization": f"Bearer {generate_jwt_token(user_id=user_id)}"
        }
    }
    # Act
    import functions.RemoveCard.app
    importlib.reload(functions.RemoveCard.app)
    response = functions.RemoveCard.app.lambda_handler(event, {})

    # Assert
    assert response['statusCode'] == 404