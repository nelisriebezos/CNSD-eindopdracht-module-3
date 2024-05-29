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
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI-Collection-Cards-In-Deck",
                    "KeySchema": [
                        {"AttributeName": "PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 1,
                        "WriteCapacityUnits": 1,
                    },
                }
            ],
        )
        yield table


@pytest.fixture()
def setup_dynamodb_collection_with_items(setup_dynamodb_collection):
    table = setup_dynamodb_collection

    table.put_item(
        Item={
            "PK": "UserId#test-user",
            "SK": "CardInstanceId#1",
            "CardFaces": [
                {
                    "M": {
                        "Colors": {"L": [{"S": "W"}]},
                        "FlavorText": {
                            "S": "Charity is rare on Innistrad, but kindness is always repaid."
                        },
                        "LowercaseFaceName": {"S": "beloved beggar"},
                        "ManaCost": {"S": "{1}{W}"},
                        "TypeLine": {"S": "Creature — Human Peasant"},
                        "ImageUrl": {
                            "S": "https://cards.scryfall.io/png/front/a/3/a3d5a0d4-1f7b-4a88-b375-b241c8e5e117.png?1673158500"
                        },
                        "FaceName": {"S": "Beloved Beggar"},
                        "OracleText": {
                            "S": "Disturb {4}{W}{W} (You may cast this card from your graveyard transformed for its disturb cost.)"
                        },
                        "LowercaseOracleText": {
                            "S": "disturb {4}{w}{w} (you may cast this card from your graveyard transformed for its disturb cost.)"
                        },
                    }
                },
                {
                    "M": {
                        "Colors": {"L": [{"S": "W"}]},
                        "FlavorText": {
                            "S": "As long as evil threatens his town, the Blessed Sleep can wait."
                        },
                        "LowercaseFaceName": {"S": "generous soul"},
                        "ManaCost": {"S": ""},
                        "TypeLine": {"S": "Creature — Spirit"},
                        "ImageUrl": {
                            "S": "https://cards.scryfall.io/png/back/a/3/a3d5a0d4-1f7b-4a88-b375-b241c8e5e117.png?1673158500"
                        },
                        "FaceName": {"S": "Generous Soul"},
                        "OracleText": {
                            "S": "Flying, vigilance\nIf Generous Soul would be put into a graveyard from anywhere, exile it instead."
                        },
                        "LowercaseOracleText": {
                            "S": "flying, vigilance\nif generous soul would be put into a graveyard from anywhere, exile it instead."
                        },
                    }
                },
            ],
            "LowerCaseOracleName": "beloved beggar // generous soul",
            "CombinedLowercaseOracleText": "disturb {4}{w}{w} (you may cast this card from your graveyard transformed for its disturb cost. // Flying, vigilance\nIf Generous Soul would be put into a graveyard from anywhere, exile it instead.",
            "OracleName": "Beloved Beggar // Generous Soul",
            "DataType": "Card",
        },
    )

    yield table


@pytest.fixture()
def setup_dynamodb_collection_with_multiple_items(setup_dynamodb_collection):
    table = setup_dynamodb_collection

    table.put_item(
        Item={
            "PK": "UserId#test-user",
            "SK": "CardInstanceId#1",
            "CardFaces": [
                {
                    "M": {
                        "Colors": {"L": [{"S": "W"}]},
                        "FlavorText": {
                            "S": "Charity is rare on Innistrad, but kindness is always repaid."
                        },
                        "LowercaseFaceName": {"S": "beloved beggar"},
                        "ManaCost": {"S": "{1}{W}"},
                        "TypeLine": {"S": "Creature — Human Peasant"},
                        "ImageUrl": {
                            "S": "https://cards.scryfall.io/png/front/a/3/a3d5a0d4-1f7b-4a88-b375-b241c8e5e117.png?1673158500"
                        },
                        "FaceName": {"S": "Beloved Beggar"},
                        "OracleText": {
                            "S": "Disturb {4}{W}{W} (You may cast this card from your graveyard transformed for its disturb cost.)"
                        },
                        "LowercaseOracleText": {
                            "S": "disturb {4}{w}{w} (you may cast this card from your graveyard transformed for its disturb cost.)"
                        },
                    }
                },
                {
                    "M": {
                        "Colors": {"L": [{"S": "W"}]},
                        "FlavorText": {
                            "S": "As long as evil threatens his town, the Blessed Sleep can wait."
                        },
                        "LowercaseFaceName": {"S": "generous soul"},
                        "ManaCost": {"S": ""},
                        "TypeLine": {"S": "Creature — Spirit"},
                        "ImageUrl": {
                            "S": "https://cards.scryfall.io/png/back/a/3/a3d5a0d4-1f7b-4a88-b375-b241c8e5e117.png?1673158500"
                        },
                        "FaceName": {"S": "Generous Soul"},
                        "OracleText": {
                            "S": "Flying, vigilance\nIf Generous Soul would be put into a graveyard from anywhere, exile it instead."
                        },
                        "LowercaseOracleText": {
                            "S": "flying, vigilance\nif generous soul would be put into a graveyard from anywhere, exile it instead."
                        },
                    }
                },
            ],
            "LowerCaseOracleName": "beloved beggar // generous soul",
            "CombinedLowercaseOracleText": "disturb {4}{w}{w} (you may cast this card from your graveyard transformed for its disturb cost. // Flying, vigilance\nIf Generous Soul would be put into a graveyard from anywhere, exile it instead.",
            "OracleName": "Beloved Beggar // Generous Soul",
            "DataType": "Card",
        },
    )

    table.put_item(
        Item={
            "PK": "UserId#test-user",
            "SK": "CardInstanceId#ed1387cd-0ff9-41fc-825c-1b1cdb6a52e1",
            "CardFaces": [
                {
                    "M": {
                        "Colors": {"L": [{"S": "R"}]},
                        "FlavorText": {
                            "S": '"That\'s a lotta nuggets."\n—Jaya Ballard, task mage'
                        },
                        "LowercaseFaceName": {"S": "chicken egg"},
                        "ManaCost": {"S": "{1}{R}"},
                        "TypeLine": {"S": "Creature — Egg"},
                        "ImageUrl": {
                            "S": "https://cards.scryfall.io/png/front/6/4/640ac565-331b-47e2-b2af-a8a94a96488a.png?1582935068"
                        },
                        "FaceName": {"S": "Chicken Egg"},
                        "OracleText": {
                            "S": "At the beginning of your upkeep, roll a six-sided die. If you roll a 6, sacrifice Chicken Egg and create a 4/4 red Giant Bird creature token."
                        },
                        "LowercaseOracleText": {
                            "S": "at the beginning of your upkeep, roll a six-sided die. if you roll a 6, sacrifice chicken egg and create a 4/4 red giant bird creature token."
                        },
                    }
                }
            ],
            "LowerCaseOracleName": "chicken egg",
            "CombinedLowercaseOracleText": "at the beginning of your upkeep, roll a six-sided die. if you roll a 6, sacrifice chicken egg and create a 4/4 red giant bird creature token.",
            "OracleName": "Chicken Egg",
            "DataType": "Card",
        }
    )
    yield table


@pytest.fixture()
def setup_dynamodb_collection_with_three_items(
    setup_dynamodb_collection_with_multiple_items,
):
    table = setup_dynamodb_collection_with_multiple_items
    table.put_item(
        Item={
            "PK": "UserId#test-user",
            "SK": "CardInstanceId#691387cd-0ff9-41fc-825c-1b1cdb6a52e1",
            "CardFaces": [
                {
                    "M": {
                        "Colors": {"L": [{"S": "R"}]},
                        "FlavorText": {
                            "S": '"That\'s a lotta nuggets."\n—Jaya Ballard, task mage'
                        },
                        "LowercaseFaceName": {"S": "chicken egg"},
                        "ManaCost": {"S": "{1}{R}"},
                        "TypeLine": {"S": "Creature — Egg"},
                        "ImageUrl": {
                            "S": "https://cards.scryfall.io/png/front/6/4/640ac565-331b-47e2-b2af-a8a94a96488a.png?1582935068"
                        },
                        "FaceName": {"S": "Chicken Egg"},
                        "OracleText": {
                            "S": "At the beginning of your upkeep, roll a six-sided die. If you roll a 6, sacrifice Chicken Egg and create a 4/4 red Giant Bird creature token."
                        },
                        "LowercaseOracleText": {
                            "S": "at the beginning of your upkeep, roll a six-sided die. if you roll a 6, sacrifice chicken egg and create a 4/4 red giant bird creature token."
                        },
                    }
                }
            ],
            "LowerCaseOracleName": "chicken egg",
            "CombinedLowercaseOracleText": "at the beginning of your upkeep, roll a six-sided die. if you roll a 6, sacrifice chicken egg and create a 4/4 red giant bird creature token.",
            "OracleName": "69 Chicken Egg",
            "DataType": "Card",
        }
    )
    yield table
