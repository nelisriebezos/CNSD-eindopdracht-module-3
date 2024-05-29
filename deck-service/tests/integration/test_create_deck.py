from _pytest.monkeypatch import MonkeyPatch
import json
import boto3
from boto3.dynamodb.conditions import Key
import uuid
from moto import mock_dynamodb
import time
from jose import jwt
import unittest

@mock_dynamodb
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
        from functions.CreateDeck import app

        return app

    def setUp(self):
        self.monkeypatch = MonkeyPatch()

        self.monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
        self.monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
        self.monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
        self.monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
        self.monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

        self.DYNAMO_DB_DECK_TABLE_NAME = "table_decks"

        self.monkeypatch.setenv("DISABLE_XRAY", "true")
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

        self.user_id = "test-user"
        self.jwt_token = self.generate_jwt_token(user_id=self.user_id)

        self.sut = self.get_sut()

    def test_deck_is_created(self):
        expected_deck_name = "Test deck"

        mock_event = {
            "body": json.dumps({
                "name": expected_deck_name,
            }),
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 201
        assert "body" in result

        body = json.loads(result["body"])

        assert "id" in body
        assert body["id"] != None
        assert body["name"] == expected_deck_name

        db_items = self.dynamodb_table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{self.user_id}") & Key("SK").begins_with("DECK#"),
        )["Items"]

        assert len(db_items) == 1
        assert db_items[0]["PK"] == f"USER#{self.user_id}"
        assert db_items[0]["SK"] == f"DECK#{body['id']}"
        assert db_items[0]["data_type"] == "DECK"
        assert db_items[0]["user_id"] == self.user_id
        assert db_items[0]["deck_id"] == body["id"]
        assert db_items[0]["deck_name"] == expected_deck_name

    def test_invalid_request_is_returned_when_no_body_is_specified(self):
        mock_event = {
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 400
        assert "body" in result

        body = json.loads(result["body"])

        assert "message" in body
        assert body["message"] == "Missing 'name'"

    def test_invalid_request_is_returned_when_no_name_is_specified(self):
        mock_event = {
            "body": json.dumps({}),
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 400
        assert "body" in result

        body = json.loads(result["body"])

        assert "message" in body
        assert body["message"] == "Missing 'name'"
