import importlib
from unittest.mock import patch
import os
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")


# !--------------------UPDATE user_id DEPENDING ON THE USER--------------------!
user_id = "c6a38601-c66c-4ef4-bc3b-554379866fbb"
# !--------------------UPDATE table_name DEPENDING ON THE STACK--------------------!
table_name = "production-mtg-collection-db"
# !--------------------UPDATE default-cards_json_path DEPENDING ON THE PATH--------------------!
default_cards_json_path = r"C:\Users\niels\Downloads\default-cards-20240125220523.json"

@patch.dict(os.environ, {"DISABLE_XRAY": "True",
                         "DYNAMODB_TABLE_NAME": table_name,
                         "CARD_JSON_LOCATION": default_cards_json_path,
                         "USERID": user_id})
def test_add_many_cards():
    import add_13000_cards.app
    importlib.reload(add_13000_cards.app)
    add_13000_cards.app.lambda_handler({}, {})