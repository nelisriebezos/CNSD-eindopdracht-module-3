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

    def insert_test_incident(self, deck_id: str, deck_name: str, user_id: str = None):
        if user_id is None:
            user_id = self.user_id

        self.dynamodb_table.put_item(Item={
            "PK": f"USER#{user_id}",
            "SK": f"DECK#{deck_id}",

            "data_type": "DECK",
            "user_id": user_id,
            "deck_id": deck_id,
            "deck_name": deck_name,
        })

    def get_sut(self):
        from functions.GetDecksFromUser import app

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

    def test_all_created_decks_are_returned_correctly(self):
        deck_id = "deck-id"
        deck_name = "deck-name"

        self.insert_test_incident(deck_id, deck_name)

        mock_event = {
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 200
        assert "body" in result
        assert result["body"] is not None

        body = json.loads( result["body"] )

        assert len(body) == 1
        assert body[0]["id"] == deck_id
        assert body[0]["name"] == deck_name

    def test_no_decks_are_returned_if_the_user_does_not_have_decks(self):
        deck_id = "deck-id"
        deck_name = "deck-name"
        other_user_id = "other-user"

        self.insert_test_incident(deck_id, deck_name, user_id=other_user_id)

        mock_event = {
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 200
        assert "body" in result
        assert result["body"] is not None

        body = json.loads( result["body"] )

        assert len(body) == 0