import boto3
import os
import pytest
from moto import mock_dynamodb
from boto3.dynamodb.conditions import Key, Attr

DYNAMODB_TABLE_NAME = "test-table"


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto. Otherwise it will deploy it for real"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture()
def setup_dynamodb_collection(aws_credentials):
    with mock_dynamodb():
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        yield table


@pytest.fixture()
def setup_dynamodb_collection_with_items(setup_dynamodb_collection):
    table = setup_dynamodb_collection

    table.put_item(
        Item={
            "PK": "OracleId#517be4da-9aa0-4a83-a559-962df0450f2c",
            "SK": "PrintId#faf65512-8228-48f4-ba7b-d861b66d28c9",
            "CardFaces": [
                {
                    "M": {
                        "Colors": {"L": [{"S": "B"}]},
                        "FlavorText": {
                            "S": '"Indulge the void. Become the void. Consume all you touch."\n—Drana, the last bloodchief'
                        },
                        "LowercaseFaceName": {"S": "oblivion's hunger"},
                        "ManaCost": {"S": "{1}{B}"},
                        "TypeLine": {"S": "Instant"},
                        "ImageUrl": {
                            "S": "https://cards.scryfall.io/png/front/f/a/faf65512-8228-48f4-ba7b-d861b66d28c9.png?1604196298"
                        },
                        "FaceName": {"S": "Oblivion's Hunger"},
                        "OracleText": {
                            "S": 'Target creature you control gains indestructible until end of turn. Draw a card if that creature has a +1/+1 counter on it. (Damage and effects that say "destroy" don\'t destroy the creature.)'
                        },
                        "LowercaseOracleText": {
                            "S": 'target creature you control gains indestructible until end of turn. draw a card if that creature has a +1/+1 counter on it. (damage and effects that say "destroy" don\'t destroy the creature.)'
                        },
                    }
                }
            ],
            "LowerCaseOracleName": "oblivion's hunger",
            "OracleName": "Oblivion's Hunger",
            "CombinedLowercaseOracleText": 'target creature you control gains indestructible until end of turn. draw a card if that creature has a +1/+1 counter on it. (damage and effects that say "destroy" don\'t destroy the creature.)',
        },
    )

    yield table
