import importlib
import json
import time
from unittest.mock import patch
import os
import boto3
from jose import jwt
from moto import mock_dynamodb
from boto3.dynamodb.conditions import Key
import pytest
import logging

logger = logging.getLogger()
logger.setLevel("INFO")


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def generate_jwt_token(
    user_id: str = "test-user",
    secret_key: str = "secret",
    algorithm: str = "HS256",
    claims: dict = {},
) -> str:
    default_claims = {
        "iss": "test_issuer",
        "sub": user_id,
        "aud": "test_audience",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
        "cognito:username": user_id,
    }

    all_claims = {**default_claims, **claims}
    token = jwt.encode(all_claims, secret_key, algorithm=algorithm)
    return token


def setup_get_card_response():
    return {
        "PK": f"OracleId#562d71b9-1646-474e-9293-55da6947a758",
        "SK": f"PrintId#67f4c93b-080c-4196-b095-6a120a221988",
        "OracleId": "562d71b9-1646-474e-9293-55da6947a758",
        "PrintId": "67f4c93b-080c-4196-b095-6a120a221988",
        "OracleName": "Agadeem's Awakening // Agadeem, the Undercrypt",
        "SetName": "Zendikar Rising",
        "ReleasedAt": "2020-09-25",
        "Rarity": "mythic",
        "DeckId": "",
        "Price": "18.27",
        "LowerCaseOracleName": "agadeem's awakening // agadeem, the undercrypt",
        "CardFaces": [
            {
                "PK": f"OracleId#562d71b9-1646-474e-9293-55da6947a758",
                "SK": f"PrintId#67f4c93b-080c-4196-b095-6a120a221988#Face#1",
                "OracleId": "562d71b9-1646-474e-9293-55da6947a758",
                "PrintId": "67f4c93b-080c-4196-b095-6a120a221988",
                "OracleText": "Return from your graveyard to the battlefield any number of target creature cards that each have a different mana value X or less.",
                "ManaCost": "{X}{B}{B}{B}",
                "TypeLine": "Sorcery",
                "FaceName": "Agadeem's Awakening",
                "FlavorText": '"Now is the death-hour, just before dawn. Wake, sleepers, and haunt the living!"\n—Vivias, Witch Vessel,',
                "ImageUrl": "https://cards.scryfall.io/png/back/6/7/67f4c93b-080c-4196-b095-6a120a221988.png?1604195226",
                "Colors": ["B"],
                "LowercaseFaceName": "agadeem's awakening",
                "LowercaseOracleText": "return from your graveyard to the battlefield any number of target creature cards that each have a different mana value x or less.",
            },
            {
                "PK": f"OracleId#562d71b9-1646-474e-9293-55da6947a758",
                "SK": f"PrintId#67f4c93b-080c-4196-b095-6a120a221988#Face#2",
                "OracleId": "562d71b9-1646-474e-9293-55da6947a758",
                "PrintId": "67f4c93b-080c-4196-b095-6a120a221988",
                "OracleText": "As Agadeem, the Undercrypt enters the battlefield, you may pay 3 life. If you don't, it enters the battlefield tapped.\n{T}: Add {B}.",
                "ManaCost": "",
                "TypeLine": "Land",
                "FaceName": "Agadeem, the Undercrypt",
                "FlavorText": '"Here below the hedron fields, souls and secrets lie entombed."\n—Vivias, Witch Vessel',
                "ImageUrl": "https://cards.scryfall.io/png/front/6/7/67f4c93b-080c-4196-b095-6a120a221988.png?1604195226",
                "Colors": [],
                "LowercaseFaceName": "agadeem, the undercrypt",
                "LowercaseOracleText": "as agadeem, the undercrypt enters the battlefield, you may pay 3 life. if you don't, it enters the battlefield tapped.\n{t}: add {b}.",
            },
        ],
    }


def setup_saved_cards_response():
    return [
        {
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
                    "FlavorText": '"Now is the death-hour, just before dawn. Wake, sleepers, and haunt the living!"\n—Vivias, Witch Vessel,',
                    "ImageUrl": "https://cards.scryfall.io/png/back/6/7/67f4c93b-080c-4196-b095-6a120a221988.png?1604195226",
                    "Colors": ["B"],
                    "LowercaseFaceName": "agadeem's awakening",
                    "LowercaseOracleText": "return from your graveyard to the battlefield any number of target creature cards that each have a different mana value x or less.",
                },
                {
                    "OracleText": "As Agadeem, the Undercrypt enters the battlefield, you may pay 3 life. If you don't, it enters the battlefield tapped.\n{T}: Add {B}.",
                    "ManaCost": "",
                    "TypeLine": "Land",
                    "FaceName": "Agadeem, the Undercrypt",
                    "FlavorText": '"Here below the hedron fields, souls and secrets lie entombed."\n—Vivias, Witch Vessel',
                    "ImageUrl": "https://cards.scryfall.io/png/front/6/7/67f4c93b-080c-4196-b095-6a120a221988.png?1604195226",
                    "Colors": [],
                    "LowercaseFaceName": "agadeem, the undercrypt",
                    "LowercaseOracleText": "as agadeem, the undercrypt enters the battlefield, you may pay 3 life. if you don't, it enters the battlefield tapped.\n{t}: add {b}.",
                },
            ],
            "GSI1SK": "",
        }
    ]


def setup_table():
    dynamodb = boto3.resource("dynamodb", "us-east-1")
    table = dynamodb.create_table(
        TableName="test-collection-table",
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.meta.client.get_waiter("table_exists").wait(TableName="test-collection-table")

    return table


@patch.dict(
    os.environ,
    {
        "DISABLE_XRAY": "True",
        "EVENT_BUS_ARN": "",
        "DYNAMODB_TABLE_NAME": "test-collection-table",
        "STAGE": "test-stage",
    },
)
@mock_dynamodb
@patch("functions.add_card.app.uuid.uuid4")
@patch("functions.add_card.app.boto3.client")
def test_lambda_handler_successful(
    mock_boto3_client, mock_uuid, aws_credentials, requests_mock
):
    # Arrange
    mocked_url = "https://mockapi.example.com"
    mock_ssm = mock_boto3_client.return_value
    mock_ssm.get_parameter.return_value = {"Parameter": {"Value": mocked_url}}

    mocked_uuid = "6c538e3f-068d-44af-9117-ef3f653831d2"
    mock_uuid.return_value = mocked_uuid

    table = setup_table()

    event = {
        "headers": {"Authorization": f"Bearer {generate_jwt_token()}"},
        "body": json.dumps(
            {
                "oracle_id": "562d71b9-1646-474e-9293-55da6947a758",
                "print_id": "67f4c93b-080c-4196-b095-6a120a221988",
                "condition": "MINT",
            }
        ),
    }

    requests_mock.get(
        f"{mocked_url}/api/cards/562d71b9-1646-474e-9293-55da6947a758/67f4c93b-080c-4196-b095-6a120a221988",
        json=setup_get_card_response(),
    )

    import functions.add_card.app

    importlib.reload(functions.add_card.app)

    # Act
    result = functions.add_card.app.lambda_handler(event, {})

    # Assert
    card = table.query(
        KeyConditionExpression=Key("PK").eq("UserId#test-user")
        & Key("SK").eq("CardInstanceId#6c538e3f-068d-44af-9117-ef3f653831d2")
    )

    assert result["statusCode"] == 201
    assert card["Items"][0]["PrintId"] == "67f4c93b-080c-4196-b095-6a120a221988"
    assert card["Items"][0]["Condition"] == "MINT"

    assert (
        card["Items"][0]["CardFaces"][0]["OracleText"]
        == "Return from your graveyard to the battlefield any number of target creature cards that each have a different mana value X or less."
    )
    assert card["Items"][0]["CardFaces"][0]["ManaCost"] == "{X}{B}{B}{B}"
    assert card["Items"][0]["CardFaces"][0]["TypeLine"] == "Sorcery"
    assert card["Items"][0]["CardFaces"][0]["FaceName"] == "Agadeem's Awakening"
    assert (
        card["Items"][0]["CardFaces"][0]["FlavorText"]
        == '"Now is the death-hour, just before dawn. Wake, sleepers, and haunt the living!"\n—Vivias, Witch Vessel,'
    )
    assert (
        card["Items"][0]["CardFaces"][0]["ImageUrl"]
        == "https://cards.scryfall.io/png/back/6/7/67f4c93b-080c-4196-b095-6a120a221988.png?1604195226"
    )
    assert card["Items"][0]["CardFaces"][0]["Colors"] == ["B"]
    assert (
        card["Items"][0]["CardFaces"][0]["LowercaseFaceName"] == "agadeem's awakening"
    )
    assert (
        card["Items"][0]["CardFaces"][0]["LowercaseOracleText"]
        == "return from your graveyard to the battlefield any number of target creature cards that each have a different mana value x or less."
    )

    assert (
        card["Items"][0]["CardFaces"][1]["OracleText"]
        == "As Agadeem, the Undercrypt enters the battlefield, you may pay 3 life. If you don't, it enters the battlefield tapped.\n{T}: Add {B}."
    )
    assert card["Items"][0]["CardFaces"][1]["ManaCost"] == ""
    assert card["Items"][0]["CardFaces"][1]["TypeLine"] == "Land"
    assert card["Items"][0]["CardFaces"][1]["FaceName"] == "Agadeem, the Undercrypt"
    assert (
        card["Items"][0]["CardFaces"][1]["FlavorText"]
        == '"Here below the hedron fields, souls and secrets lie entombed."\n—Vivias, Witch Vessel'
    )
    assert (
        card["Items"][0]["CardFaces"][1]["ImageUrl"]
        == "https://cards.scryfall.io/png/front/6/7/67f4c93b-080c-4196-b095-6a120a221988.png?1604195226"
    )
    assert card["Items"][0]["CardFaces"][1]["Colors"] == []
    assert (
        card["Items"][0]["CardFaces"][1]["LowercaseFaceName"]
        == "agadeem, the undercrypt"
    )
    assert (
        card["Items"][0]["CardFaces"][1]["LowercaseOracleText"]
        == "as agadeem, the undercrypt enters the battlefield, you may pay 3 life. if you don't, it enters the battlefield tapped.\n{t}: add {b}."
    )


@patch.dict(
    os.environ,
    {
        "DISABLE_XRAY": "True",
        "EVENT_BUS_ARN": "",
        "DYNAMODB_TABLE_NAME": "test-collection-table",
        "STAGE": "test-stage",
    },
)
@mock_dynamodb
@patch("functions.add_card.app.uuid.uuid4")
@patch("functions.add_card.app.boto3.client")
def test_lambda_handler_card_not_found(
    mock_boto3_client, mock_uuid, aws_credentials, requests_mock
):
    # Arrange
    mocked_url = "https://mockapi.example.com"
    mock_ssm = mock_boto3_client.return_value
    mock_ssm.get_parameter.return_value = {"Parameter": {"Value": f"{mocked_url}"}}

    mocked_uuid = "6c538e3f-068d-44af-9117-ef3f653831d2"
    mock_uuid.return_value = mocked_uuid

    event = {
        "headers": {"Authorization": f"Bearer {generate_jwt_token()}"},
        "body": json.dumps(
            {"oracle_id": "wrong-id", "print_id": "wrong-id", "condition": "MINT"}
        ),
    }

    requests_mock.get(
        f"{mocked_url}/api/cards/wrong-id/wrong-id",
        json={"Message": "Card not found."},
        status_code=404,
    )

    import functions.add_card.app

    importlib.reload(functions.add_card.app)

    # Act
    result = functions.add_card.app.lambda_handler(event, {})
    response_body = json.loads(result["body"])

    # Assert
    assert result["statusCode"] == 404
    assert response_body["Message"] == "Card not found."
