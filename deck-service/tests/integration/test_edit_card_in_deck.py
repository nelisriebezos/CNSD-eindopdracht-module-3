from _pytest.monkeypatch import MonkeyPatch
import json
import boto3
from boto3.dynamodb.conditions import Key
from uuid import uuid4
from moto import mock_dynamodb, mock_ssm
import time
from jose import jwt
import unittest
import responses
from typing import List

# Card oracles {{{
CARD_ORACLE_1 = lambda oracle_id: {
    "OracleName": "Ghoulcaller Gisa",
    "OracleId": oracle_id,
    "SetName": "Commander 2014",
    "PrintId": "bbd9aba4-6db6-417b-8515-5617f0acdc9b",
    "CardFaces": [
        {
            "Colors": [
                "B"
            ],
            "FlavorText": "\"Geralf, must you always whine? I agreed to nothing. I'll raise ghouls anytime I wish.\"",
            "LowercaseFaceName": "ghoulcaller gisa",
            "ManaCost": "{3}{B}{B}",
            "TypeLine": "Legendary Creature — Human Wizard",
            "ImageUrl": "https://cards.scryfall.io/png/front/b/b/bbd9aba4-6db6-417b-8515-5617f0acdc9b.png?1561956636",
            "FaceName": "Ghoulcaller Gisa",
            "OracleText": "{B}, {T}, Sacrifice another creature: Create X 2/2 black Zombie creature tokens, where X is the sacrificed creature's power.",
            "LowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power."
        }
    ],
    "Rarity": "mythic",
    "ReleasedAt": "2014-11-07",
    "Price": "2.52",
    "SK": "PrintId#bbd9aba4-6db6-417b-8515-5617f0acdc9b",
    "CombinedLowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power. ",
    "PK": "OracleId#0dd894cb-1968-471c-af08-ea7ec5ce8428",
    "LowerCaseOracleName": "ghoulcaller gisa"
}
# }}}

@mock_dynamodb
@mock_ssm
class TestCreateDeck(unittest.TestCase):
    def generate_jwt_token(self, user_id: str = "test-user", secret_key: str = "secret", algorithm: str = "HS256", claims: dict = {}) -> str:
        default_claims = {
            'iss': 'test_issuer',
            'sub': user_id,
            'aud': 'test_audience',
            'exp': int(time.time()) + 3600,
            'iat': int(time.time()),
            'cognito:username': user_id
        }

        # Merge default and user-provided claims
        all_claims = {**default_claims, **claims}

        # Generate JWT
        token = jwt.encode(all_claims, secret_key, algorithm=algorithm)

        return token

    def get_sut(self):
        from functions.EditDeckCard import app

        return app

    def setUp(self):
        responses.reset()

        self.monkeypatch = MonkeyPatch()

        self.monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
        self.monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
        self.monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
        self.monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
        self.monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

        self.DYNAMO_DB_DECK_TABLE_NAME = "table_decks"
        self.STAGE = "test"
        self.CARD_ENDPOINT = "http://deck-service"

        self.monkeypatch.setenv("DISABLE_XRAY", "true")
        self.monkeypatch.setenv("STAGE", self.STAGE)
        self.monkeypatch.setenv("DYNAMO_DB_DECK_TABLE_NAME", self.DYNAMO_DB_DECK_TABLE_NAME)

        self.dynamodb_client = boto3.client("dynamodb")

        self.dynamodb_client.create_table( # {{{
            TableName=self.DYNAMO_DB_DECK_TABLE_NAME,
            KeySchema=[
                {
                    "AttributeName": "PK",
                    "KeyType": "HASH",
                },
                {
                    "AttributeName": "SK",
                    "KeyType": "RANGE",
                },
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "PK",
                    "AttributeType": "S",
                },
                {
                    "AttributeName": "SK",
                    "AttributeType": "S",
                },
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )
        # }}}
        self.dynamodb_table = boto3.resource("dynamodb").Table(self.DYNAMO_DB_DECK_TABLE_NAME)

        self.ssm_client = boto3.client("ssm")

        self.ssm_client.put_parameter(
            Name=f"/{self.STAGE}/MTGCardApi/url",
            Type="String",
            Value=self.CARD_ENDPOINT,
        )

        self.user_id = "test-user"
        self.jwt_token = self.generate_jwt_token(user_id=self.user_id)

        self.sut = self.get_sut()

    def assert_db_deck_card_oracle_keys_equal_to_expected_oracle(self, actual: dict, expected_oracle: dict):
        for key in expected_oracle.keys():
            if key != "CardFaces" and key not in self.sut.DISALLOWED_DB_KEYS:
                assert key in actual

                assert actual[key] == expected_oracle[key]

        for i in range( len( expected_oracle["CardFaces"] ) ):
            expected_card_face = expected_oracle["CardFaces"][i]

            for key in expected_card_face.keys():
                if key not in self.sut.DISALLOWED_DB_KEYS:
                    actual_card_face = actual["CardFaces"][i]

                    assert key in actual_card_face

                    assert actual_card_face[key] == expected_card_face[key]

    def test_card_print_is_changed_when_new_card_print_is_specified(self):
        oracle_id = "0dd894cb-1968-471c-af08-ea7ec5ce8428"
        deck_card_id = str( uuid4() )
        mock_card_oracle_response = CARD_ORACLE_1(oracle_id)
        deck_id = "some-deck-id"
        card_location = self.sut.AVAILABLE_DECK_LOCATIONS[0]

        original_card_instance_id = str( uuid4() )
        new_card_instance_id = str( uuid4() )
        original_card_print_id = str( uuid4() )
        new_card_print_id = mock_card_oracle_response["PrintId"]

        get_cards_by_oracle_request = responses.add(
            responses.GET,
            f"{self.CARD_ENDPOINT}/api/cards/{oracle_id}/{new_card_print_id}/",
            status=200,
            json=mock_card_oracle_response,
        )

        self.dynamodb_table.put_item(Item={
            "PK": f"USER#{self.user_id}#DECK#{deck_id}",
            "SK": f"DECK_CARD#{deck_card_id}",

            "data_type": "DECK_CARD",
            "user_id": self.user_id,
            "deck_id": deck_id,
            "deck_card_id": deck_card_id,
            "card_location": card_location,
            "card_instance_id": original_card_instance_id,

            "PrintId": original_card_print_id,
            "OracleId": oracle_id,
        })

        mock_event = {
            "body": json.dumps({
                "cardLocation": card_location,
                "cardInstanceId": new_card_instance_id,
                "cardPrintId": new_card_print_id,
            }),
            "pathParameters": {
                "deck_id": deck_id,
                "card_id": deck_card_id,
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert get_cards_by_oracle_request.call_count == 1

        assert result["statusCode"] == 204
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert body is None

        db_items = self.dynamodb_table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{self.user_id}#DECK#{deck_id}")
        )["Items"]

        assert len(db_items) == 1

        assert db_items[0]["PK"] == f"USER#{self.user_id}#DECK#{deck_id}"
        assert "DECK_CARD#" in db_items[0]["SK"]

        assert db_items[0]["data_type"] == "DECK_CARD"
        assert db_items[0]["user_id"] == self.user_id
        assert db_items[0]["deck_id"] == deck_id
        assert db_items[0]["card_location"] == card_location
        assert db_items[0]["card_instance_id"] == new_card_instance_id

        assert db_items[0]["PrintId"] == new_card_print_id
        assert db_items[0]["OracleId"] == oracle_id

        self.assert_db_deck_card_oracle_keys_equal_to_expected_oracle(db_items[0], mock_card_oracle_response)

    def test_card_location_is_changed_when_new_card_location_is_specified(self):
        oracle_id = "0dd894cb-1968-471c-af08-ea7ec5ce8428"
        deck_card_id = str( uuid4() )
        mock_card_oracle_response = CARD_ORACLE_1(oracle_id)
        deck_id = "some-deck-id"

        original_card_instance_id = str( uuid4() )
        original_card_print_id = mock_card_oracle_response["PrintId"]
        original_card_location = self.sut.AVAILABLE_DECK_LOCATIONS[0]
        new_card_location = self.sut.AVAILABLE_DECK_LOCATIONS[1]

        get_cards_by_oracle_request = responses.add(
            responses.GET,
            f"{self.CARD_ENDPOINT}/api/cards/{oracle_id}/{original_card_print_id}/",
            status=500,
        )

        self.dynamodb_table.put_item(Item={
            "PK": f"USER#{self.user_id}#DECK#{deck_id}",
            "SK": f"DECK_CARD#{deck_card_id}",

            "data_type": "DECK_CARD",
            "user_id": self.user_id,
            "deck_id": deck_id,
            "deck_card_id": deck_card_id,
            "card_location": original_card_location,
            "card_instance_id": original_card_instance_id,

            "PrintId": original_card_print_id,
            "OracleId": oracle_id,
        })

        mock_event = {
            "body": json.dumps({
                "cardLocation": new_card_location,
                "cardInstanceId": original_card_instance_id,
                "cardPrintId": original_card_print_id,
            }),
            "pathParameters": {
                "deck_id": deck_id,
                "card_id": deck_card_id,
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 204
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert body is None

        assert get_cards_by_oracle_request.call_count == 0

        db_items = self.dynamodb_table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{self.user_id}#DECK#{deck_id}")
        )["Items"]

        assert len(db_items) == 1

        assert db_items[0]["PK"] == f"USER#{self.user_id}#DECK#{deck_id}"
        assert "DECK_CARD#" in db_items[0]["SK"]

        assert db_items[0]["data_type"] == "DECK_CARD"
        assert db_items[0]["user_id"] == self.user_id
        assert db_items[0]["deck_id"] == deck_id
        assert db_items[0]["card_location"] == new_card_location
        assert db_items[0]["card_instance_id"] == original_card_instance_id

        assert db_items[0]["PrintId"] == original_card_print_id
        assert db_items[0]["OracleId"] == oracle_id

    def test_bad_request_is_returned_if_no_card_print_is_found(self):
        oracle_id = "0dd894cb-1968-471c-af08-ea7ec5ce8428"
        deck_card_id = str( uuid4() )
        mock_card_oracle_response = CARD_ORACLE_1(oracle_id)
        deck_id = "some-deck-id"
        card_location = self.sut.AVAILABLE_DECK_LOCATIONS[0]

        original_card_instance_id = str( uuid4() )
        new_card_instance_id = str( uuid4() )
        original_card_print_id = str( uuid4() )
        new_card_print_id = mock_card_oracle_response["PrintId"]

        get_cards_by_oracle_request = responses.add(
            responses.GET,
            f"{self.CARD_ENDPOINT}/api/cards/{oracle_id}/{new_card_print_id}/",
            status=404,
        )

        self.dynamodb_table.put_item(Item={
            "PK": f"USER#{self.user_id}#DECK#{deck_id}",
            "SK": f"DECK_CARD#{deck_card_id}",

            "data_type": "DECK_CARD",
            "user_id": self.user_id,
            "deck_id": deck_id,
            "deck_card_id": deck_card_id,
            "card_location": card_location,
            "card_instance_id": original_card_instance_id,

            "PrintId": original_card_print_id,
            "OracleId": oracle_id,
        })

        mock_event = {
            "body": json.dumps({
                "cardLocation": card_location,
                "cardInstanceId": new_card_instance_id,
                "cardPrintId": new_card_print_id,
            }),
            "pathParameters": {
                "deck_id": deck_id,
                "card_id": deck_card_id,
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 400
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "message" in body
        assert body["message"] == f"No card with oracle '{oracle_id}' and print '{new_card_print_id}' found"

        assert get_cards_by_oracle_request.call_count == 1

    def test_lambda_returns_bad_request_when_no_body_is_send(self):
        mock_event = {
            "pathParameters": {
                "deck_id": str( uuid4() ),
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 400
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "message" in body
        assert body["message"] == "Missing body in request"

    def test_lambda_returns_bad_request_when_empty_body_is_send(self):
        mock_event = {
            "body": json.dumps({}),
            "pathParameters": {
                "deck_id": str( uuid4() ),
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 400
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "message" in body
        assert body["message"] == "Missing 'cardLocation'"

    def test_lambda_returns_bad_request_when_no_card_location_is_send(self):
        mock_event = {
            "body": json.dumps({
                "cardOracle": str( uuid4() ),
            }),
            "pathParameters": {
                "deck_id": str( uuid4() ),
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 400
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "message" in body
        assert body["message"] == "Missing 'cardLocation'"

    def test_lambda_returns_bad_request_when_invalid_card_location_is_send(self):
        card_location = "invalid-location"

        mock_event = {
            "body": json.dumps({
                "cardOracle": str( uuid4() ),
                "cardLocation": card_location,
            }),
            "pathParameters": {
                "deck_id": str( uuid4() ),
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 400
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "message" in body
        assert  f"Invalid deck location: '{card_location}'. Expected one of: " in body["message"]

    def test_lambda_returns_bad_request_when_an_instance_id_is_send_without_a_print_id(self):
        mock_event = {
            "body": json.dumps({
                "cardOracle": str( uuid4() ),
                "cardInstanceId": str( uuid4() ),
                "cardLocation": self.sut.AVAILABLE_DECK_LOCATIONS[0],
            }),
            "pathParameters": {
                "deck_id": str( uuid4() ),
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 400
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "message" in body
        assert body["message"] == "'cardPrintId' should be set when 'cardInstanceId' is set"
