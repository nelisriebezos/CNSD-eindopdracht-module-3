import json
import os
from unittest.mock import patch
from .conftest import DYNAMODB_TABLE_NAME


@patch.dict(os.environ, {"DYNAMODB_TABLE_NAME": DYNAMODB_TABLE_NAME, "DISABLE_XRAY": "True"})
def test_get_card_by_id(setup_dynamodb):
    from functions.get_card.app import lambda_handler

    # Insert mock data into the table
    table = setup_dynamodb
    for card in setup_items():
        table.put_item(Item=card)

    # Mock API Gateway event
    event = {'pathParameters': {'oracle_id': '562d71b9-1646-474e-9293-55da6947a758', 'print_id': '67f4c93b-080c-4196-b095-6a120a221988'}}

    # Invoke the lambda handler
    response = lambda_handler(event, {})

    # Assert the response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['CardFaces']) == 2


@patch.dict(os.environ, {"DYNAMODB_TABLE_NAME": DYNAMODB_TABLE_NAME, "DISABLE_XRAY": "True"})
def test_get_card_by_id_not_found(setup_dynamodb):
    from functions.get_card.app import lambda_handler

    # Insert mock data into the table
    table = setup_dynamodb
    for card in setup_items():
        table.put_item(Item=card)

    # Mock API Gateway event
    event = {'pathParameters': {'oracle_id': '562d71b9-1646-474e-9293-55da6947a758', 'print_id': '0dd894cb-1968-471c-af08-ea7ec5ce8428'}}

    # Invoke the lambda handler
    response = lambda_handler(event, {})

    # Assert the response
    assert response['statusCode'] == 404


def setup_items():
    return [
        {
            "PK": f'OracleId#562d71b9-1646-474e-9293-55da6947a758',
            "SK": f'PrintId#67f4c93b-080c-4196-b095-6a120a221988',
            "OracleId": "562d71b9-1646-474e-9293-55da6947a758",
            "PrintId": "67f4c93b-080c-4196-b095-6a120a221988",
            "OracleName": "Agadeem's Awakening // Agadeem, the Undercrypt",
            "SetName": "Zendikar Rising",
            "ReleasedAt": "2020-09-25",
            "Rarity": "mythic",
            "Price": "18.27",
            "LowerCaseOracleName": "agadeem's awakening // agadeem, the undercrypt",
            "CardFaces": [
                {
                    "PK": f'OracleId#562d71b9-1646-474e-9293-55da6947a758',
                    "SK": f'PrintId#67f4c93b-080c-4196-b095-6a120a221988#Face#1',
                    "OracleId": "562d71b9-1646-474e-9293-55da6947a758",
                    "PrintId": "67f4c93b-080c-4196-b095-6a120a221988",
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
                    "PK": f'OracleId#562d71b9-1646-474e-9293-55da6947a758',
                    "SK": f'PrintId#67f4c93b-080c-4196-b095-6a120a221988#Face#2',
                    "OracleId": "562d71b9-1646-474e-9293-55da6947a758",
                    "PrintId": "67f4c93b-080c-4196-b095-6a120a221988",
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
    ]
