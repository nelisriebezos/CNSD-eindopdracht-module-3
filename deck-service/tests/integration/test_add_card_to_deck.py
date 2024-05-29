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
CARD_ORACLE_2 = lambda oracle_id: {
    "OracleName": "Ghoulcaller Gisa",
    "OracleId": oracle_id,
    "SetName": "Jumpstart",
    "PrintId": "0bcba8d3-725b-49f9-8281-eafac15208c5",
    "CardFaces": [
        {
            "Colors": [
                "B"
            ],
            "FlavorText": "\"Geralf, must you always whine? I agreed to nothing. I'll raise ghouls anytime I wish.\"",
            "LowercaseFaceName": "ghoulcaller gisa",
            "ManaCost": "{3}{B}{B}",
            "TypeLine": "Legendary Creature — Human Wizard",
            "ImageUrl": "https://cards.scryfall.io/png/front/0/b/0bcba8d3-725b-49f9-8281-eafac15208c5.png?1600700375",
            "FaceName": "Ghoulcaller Gisa",
            "OracleText": "{B}, {T}, Sacrifice another creature: Create X 2/2 black Zombie creature tokens, where X is the sacrificed creature's power.",
            "LowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power."
        }
    ],
    "Rarity": "mythic",
    "ReleasedAt": "2020-07-17",
    "Price": "1.24",
    "SK": "PrintId#0bcba8d3-725b-49f9-8281-eafac15208c5",
    "CombinedLowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power. ",
    "PK": "OracleId#0dd894cb-1968-471c-af08-ea7ec5ce8428",
    "LowerCaseOracleName": "ghoulcaller gisa"
}
CARD_ORACLE_3 = lambda oracle_id: {
    "OracleName": "Ghoulcaller Gisa",
    "OracleId": oracle_id,
    "SetName": "Commander Collection: Black",
    "PrintId": "779e3944-4342-4151-9963-87e8d41fd2ff",
    "CardFaces": [
        {
            "Colors": [
                "B"
            ],
            "FlavorText": "\"Come now, dear brother. If you wanted rules, you should have called it a *game*, not a *war*.\"\n—Gisa, to Geralf",
            "LowercaseFaceName": "ghoulcaller gisa",
            "ManaCost": "{3}{B}{B}",
            "TypeLine": "Legendary Creature — Human Wizard",
            "ImageUrl": "https://cards.scryfall.io/png/front/7/7/779e3944-4342-4151-9963-87e8d41fd2ff.png?1680135257",
            "FaceName": "Ghoulcaller Gisa",
            "OracleText": "{B}, {T}, Sacrifice another creature: Create X 2/2 black Zombie creature tokens, where X is the sacrificed creature's power.",
            "LowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power."
        }
    ],
    "Rarity": "mythic",
    "ReleasedAt": "2022-01-28",
    "Price": "1.08",
    "SK": "PrintId#779e3944-4342-4151-9963-87e8d41fd2ff",
    "CombinedLowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power. ",
    "PK": "OracleId#0dd894cb-1968-471c-af08-ea7ec5ce8428",
    "LowerCaseOracleName": "ghoulcaller gisa"
}
CARD_ORACLE_4 = lambda oracle_id: {
    "OracleName": "Ghoulcaller Gisa",
    "OracleId": oracle_id,
    "SetName": "Commander Masters",
    "PrintId": "44d7906e-8a89-4644-acb5-46fbe97ab39f",
    "CardFaces": [
        {
            "Colors": [
                "B"
            ],
            "FlavorText": "\"Geralf, must you always whine? I agreed to nothing. I'll raise ghouls anytime I wish.\"",
            "LowercaseFaceName": "ghoulcaller gisa",
            "ManaCost": "{3}{B}{B}",
            "TypeLine": "Legendary Creature — Human Wizard",
            "ImageUrl": "https://cards.scryfall.io/png/front/4/4/44d7906e-8a89-4644-acb5-46fbe97ab39f.png?1689997183",
            "FaceName": "Ghoulcaller Gisa",
            "OracleText": "{B}, {T}, Sacrifice another creature: Create X 2/2 black Zombie creature tokens, where X is the sacrificed creature's power.",
            "LowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power."
        }
    ],
    "Rarity": "rare",
    "ReleasedAt": "2023-08-04",
    "Price": "0.78",
    "SK": "PrintId#44d7906e-8a89-4644-acb5-46fbe97ab39f",
    "CombinedLowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power. ",
    "PK": "OracleId#0dd894cb-1968-471c-af08-ea7ec5ce8428",
    "LowerCaseOracleName": "ghoulcaller gisa"
}
CARD_ORACLE_5 = lambda oracle_id: {
    "OracleName": "Ghoulcaller Gisa",
    "OracleId": oracle_id,
    "SetName": "Commander Masters",
    "PrintId": "5219ed86-eb4e-43f5-9c75-f3b24abe42a5",
    "CardFaces": [
        {
            "Colors": [
                "B"
            ],
            "FlavorText": "\"Geralf, must you always whine? I agreed to nothing. I'll raise ghouls anytime I wish.\"",
            "LowercaseFaceName": "ghoulcaller gisa",
            "ManaCost": "{3}{B}{B}",
            "TypeLine": "Legendary Creature — Human Wizard",
            "ImageUrl": "https://cards.scryfall.io/png/front/5/2/5219ed86-eb4e-43f5-9c75-f3b24abe42a5.png?1690000805",
            "FaceName": "Ghoulcaller Gisa",
            "OracleText": "{B}, {T}, Sacrifice another creature: Create X 2/2 black Zombie creature tokens, where X is the sacrificed creature's power.",
            "LowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power."
        }
    ],
    "Rarity": "rare",
    "ReleasedAt": "2023-08-04",
    "Price": "0.00",
    "SK": "PrintId#5219ed86-eb4e-43f5-9c75-f3b24abe42a5",
    "CombinedLowercaseOracleText": "{b}, {t}, sacrifice another creature: create x 2/2 black zombie creature tokens, where x is the sacrificed creature's power. ",
    "PK": "OracleId#0dd894cb-1968-471c-af08-ea7ec5ce8428",
    "LowerCaseOracleName": "ghoulcaller gisa"
}
# }}}

def get_mock_card_oracles_response(oracle_id: str) -> List[dict]:
    return { # {{{
        "Items": [
            # Sort in random order
            CARD_ORACLE_3(oracle_id),
            CARD_ORACLE_2(oracle_id),
            CARD_ORACLE_5(oracle_id),
            CARD_ORACLE_4(oracle_id),
            CARD_ORACLE_1(oracle_id),
        ]
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
        from functions.AddCardToDeck import app

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

    def test_card_oracle_without_card_instance_is_successfully_added_to_deck(self):
        oracle_id = "0dd894cb-1968-471c-af08-ea7ec5ce8428"
        deck_id = "some-deck-id"
        card_location = self.sut.AVAILABLE_DECK_LOCATIONS[0]

        get_cards_by_oracle_request = responses.add(
            responses.GET,
            f"{self.CARD_ENDPOINT}/api/cards/{oracle_id}/",
            status=200,
            json=get_mock_card_oracles_response(oracle_id),
        )

        mock_event = {
            "body": json.dumps({
                "cardOracle": oracle_id,
                "cardLocation": card_location,
            }),
            "pathParameters": {
                "deck_id": deck_id,
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 201
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "deck_card_id" in body
        assert body["deck_card_id"] is not None

        assert get_cards_by_oracle_request.call_count == 1

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
        assert "card_instance_id" not in db_items[0]

        expected_oracle = CARD_ORACLE_5(oracle_id)

        self.assert_db_deck_card_oracle_keys_equal_to_expected_oracle(db_items[0], expected_oracle)

    def test_card_oracle_with_card_instance_is_successfully_added_to_deck(self):
        oracle_id = "0dd894cb-1968-471c-af08-ea7ec5ce8428"
        card_instance_id = str( uuid4() )
        mock_card_oracle_response = CARD_ORACLE_3(oracle_id)
        card_print_id = mock_card_oracle_response["PrintId"]
        deck_id = "some-deck-id"
        card_location = self.sut.AVAILABLE_DECK_LOCATIONS[0]

        get_cards_by_oracle_request = responses.add(
            responses.GET,
            f"{self.CARD_ENDPOINT}/api/cards/{oracle_id}/{card_print_id}/",
            status=200,
            json=mock_card_oracle_response,
        )

        mock_event = {
            "body": json.dumps({
                "cardOracle": oracle_id,
                "cardLocation": card_location,
                "cardInstanceId": card_instance_id,
                "cardPrintId": card_print_id,
            }),
            "pathParameters": {
                "deck_id": deck_id,
            },
            "headers": {
                "Authorization": f"Bearer {self.jwt_token}",
            },
        }
        mock_context = {}

        result = self.sut.lambda_handler(mock_event, mock_context)

        assert result["statusCode"] == 201
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "deck_card_id" in body
        assert body["deck_card_id"] is not None

        assert get_cards_by_oracle_request.call_count == 1

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
        assert db_items[0]["card_instance_id"] == card_instance_id

        self.assert_db_deck_card_oracle_keys_equal_to_expected_oracle(db_items[0], mock_card_oracle_response)

    def test_lambda_returns_not_found_when_no_existing_oracle_id_is_send(self):
        oracle_id = "non-existent"

        get_cards_by_oracle_request = responses.add(
            responses.GET,
            f"{self.CARD_ENDPOINT}/api/cards/{oracle_id}/",
            status=404,
            json={
                "Message": "Card not found.",
            },
        )

        mock_event = {
            "body": json.dumps({
                "cardOracle": oracle_id,
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

        assert result["statusCode"] == 404
        assert "body" in result
        assert result["body"] is not None

        body = json.loads(result["body"])

        assert "message" in body
        assert body["message"] == f"Card with oracle with id '{oracle_id}' was not found"

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
        assert body["message"] == "Missing 'cardOracle'"

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
