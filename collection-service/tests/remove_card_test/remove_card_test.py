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
        TableName='test-collection-table',
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

def get_card_obect():
    return {
        "PK": "UserId#1",
        "SK": "CardInstanceId#6c538e3f-068d-44af-9117-ef3f653831d2",
        "PrintId": "67f4c93b-080c-4196-b095-6a120a221988",
        "CardInstanceId": "6c538e3f-068d-44af-9117-ef3f653831d2",
        "Condition": "MINT",
        "DeckId": "",
        "OracleName": "Agadeem's Awakening // Agadeem, the Undercrypt",
        "SetName": "Zendikar Rising",
        "ReleasedAt": "2020-09-25",
        "Rarity": "mythic",
        "Price": "18.27",
        "LowerCaseOracleName": "agadeem's awakening // agadeem, the undercrypt",
        "CardFaces": [
            {
                "OracleText": "Return from your graveyard to the battlefield any number of target creature cards that each have a different mana value X or less.",
                "ManaCost": "{X}{B}{B}{B}",
                "TypeLine": "Sorcery",
                "FaceName": "Agadeem's Awakening",
                "FlavorText": "\"Now is the death-hour, just before dawn. Wake, sleepers, and haunt the living!\"\n—Vivias, Witch Vessel,",
                "ImageUrl": "https://cards.scryfall.io/png/back/6/7/67f4c93b-080c-4196-b095-6a120a221988.png?1604195226",
                "Colors": ['B'],
                "LowercaseFaceName": "agadeem's awakening",
                "LowercaseOracleText": "return from your graveyard to the battlefield any number of target creature cards that each have a different mana value x or less.",
            },
            {
                "OracleText": "As Agadeem, the Undercrypt enters the battlefield, you may pay 3 life. If you don't, it enters the battlefield tapped.\n{T}: Add {B}.",
                "ManaCost": "",
                "TypeLine": "Land",
                "FaceName": "Agadeem, the Undercrypt",
                "FlavorText": "\"Here below the hedron fields, souls and secrets lie entombed.\"\n—Vivias, Witch Vessel",
                "ImageUrl": "https://cards.scryfall.io/png/front/6/7/67f4c93b-080c-4196-b095-6a120a221988.png?1604195226",
                "Colors": [],
                "LowercaseFaceName": "agadeem, the undercrypt",
                "LowercaseOracleText": "as agadeem, the undercrypt enters the battlefield, you may pay 3 life. if you don't, it enters the battlefield tapped.\n{t}: add {b}."
            }
        ]
    }

@patch.dict(os.environ, {"DISABLE_XRAY": "True",
                         "EVENT_BUS_ARN": "",
                         "DYNAMODB_TABLE_NAME": "test-collection-table"})
@mock_dynamodb
def test_remove_card_successfull(aws_credentials):
    # Arrange
    table = setup_table()

    event = {
        "pathParameters": {
            "instance_id": "6c538e3f-068d-44af-9117-ef3f653831d2"
        },
        "headers": {
            "Authorization": f"Bearer {generate_jwt_token(user_id='1')}"
        }
    }

    put_response = table.put_item(Item=get_card_obect())

    response = table.query(
        KeyConditionExpression=Key('PK').eq('UserId#1') &
                               Key('SK').eq('CardInstanceId#6c538e3f-068d-44af-9117-ef3f653831d2'),
    )

    assert len(response['Items']) == 1

    # Act
    import functions.remove_card.app
    importlib.reload(functions.remove_card.app)
    functions.remove_card.app.lambda_handler(event, {})

    # Assert
    response = table.query(
        KeyConditionExpression=Key('PK').eq('UserId#1') &
                               Key('SK').eq('CardInstanceId#6c538e3f-068d-44af-9117-ef3f653831d2'),
    )

    assert put_response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert len(response['Items']) == 0



@patch.dict(os.environ, {"DISABLE_XRAY": "True",
                         "EVENT_BUS_ARN": "",
                         "DYNAMODB_TABLE_NAME": "test-collection-table"})
@mock_dynamodb
def test_remove_non_existent_card(aws_credentials):
    # Arrange
    table = setup_table()

    event = {
        "pathParameters": {
            "instance_id": "6c538e3f-068d-44af-9117-ef3f653831d2"
        },
        "headers": {
            "Authorization": f"Bearer {generate_jwt_token(user_id='1')}"
        }
    }

    # Act
    import functions.remove_card.app
    importlib.reload(functions.remove_card.app)
    response = functions.remove_card.app.lambda_handler(event, {})

    # Assert
    assert response['statusCode'] == 404

