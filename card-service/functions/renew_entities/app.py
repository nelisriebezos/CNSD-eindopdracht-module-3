import os
import time
from os import environ
from aws_xray_sdk.core import patch_all
import boto3
import logging
import requests
import ijson

if 'DISABLE_XRAY' not in environ:
    patch_all()

dynamodb = boto3.resource('dynamodb', 'us-east-1')
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
update_frequency_days = os.getenv("CARDS_UPDATE_FREQUENCY")

table = dynamodb.Table(DYNAMODB_TABLE_NAME)

event_bus = boto3.client('events')
logger = logging.getLogger()
logger.setLevel("INFO")

ttlOffSetSecs = (3 * 60 * 60)
local_filename = os.getenv("CARD_JSON_LOCATION", "/tmp/default-cards.json")


def turnCardIntoFaceItem(card):
    image_uris = card.get('image_uris')
    return {
        "OracleText": card.get('oracle_text', ''),
        "ManaCost": card.get('mana_cost', ''),
        "TypeLine": card.get('type_line', ''),
        "FaceName": card.get('name', ''),
        "FlavorText": card.get('flavor_text', ''),
        "ImageUrl": image_uris.get('png', ''),
        "Colors": card.get('colors', []),
        "LowercaseFaceName": str.lower(card.get('name', '')),
        "LowercaseOracleText": str.lower(card.get('oracle_text', ''))
    }


def turn_face_into_face_item(face, card_image_uri, card_colors):
    return {
        "OracleText": face.get('oracle_text', ''),
        "ManaCost": face.get('mana_cost', ''),
        "TypeLine": face.get('type_line', ''),
        "FaceName": face.get('name', ''),
        "FlavorText": face.get('flavor_text', ''),
        "ImageUrl": card_image_uri,
        "Colors": card_colors,
        "LowercaseFaceName": str.lower(face.get('name', '')),
        "LowercaseOracleText": str.lower(face.get('oracle_text', ''))
    }


def createCardInfo(card, oracle_id):
    if card['prices']['eur'] is None:
        card['prices']['eur'] = '0.00'
    try:
        return {
            "PK": f'OracleId#{oracle_id}',
            "SK": f'PrintId#{card["id"]}',
            "OracleName": card['name'],
            "SetName": card['set_name'],
            "ReleasedAt": card['released_at'],
            "Rarity": card['rarity'],
            "Price": card['prices']['eur'],
            "OracleId": oracle_id,
            "PrintId": card['id'],
            "LowerCaseOracleName": str.lower(card.get('name', ''))
        }
    except Exception as error:
        logger.error(f"An error has occurred while processing card: \n{card}\n "
                     f"Error: \n {error}")


def getOracleFromCard(card):
    if card.get('layout', '') == 'reversible_card':
        return card['card_faces'][0]['oracle_id']
    else:
        return card['oracle_id']

def getCombinedLowerCaseOracleText(faces):
    loweredText = "";
    for face in faces:
        loweredText += str.lower(face.get('OracleText', ''))
        loweredText += " "
    return loweredText


# Can only handle 25 items at a time!
def writeBatchToDb(items, table, ttl):
    with table.batch_writer() as batch:
        for item in items:
            item['RemoveAt'] = ttl
            response = batch.put_item(
                Item=item
            )


def calculateTTL(offsetInSeconds, update_frequency_days):
    currentEpochInSeconds = int(time.time())
    return currentEpochInSeconds + offsetInSeconds + int(update_frequency_days) * 24 * 60 * 60


def cutTheListAndPersist(item_list, ttl):
    if len(item_list) < 25:
        return item_list

    to_be_persisted = item_list[:25]
    to_be_continued = item_list[25:]

    writeBatchToDb(to_be_persisted, table, ttl)
    return to_be_continued


def countPersistedItems(amount):
    global persistedCounter
    persistedCounter += amount


def get_image_uri_from_face(card):
    if card.get("card_faces") is not None:
        if 'image_uris' in card['card_faces'][0]:
            return True
        else:
            return False
    else:
        return False

def get_Colors_from_face(card):
    if card.get("card_faces") is not None:
        if 'colors' in card['card_faces'][0]:
            return True
        else:
            return False
    else:
        return False


def is_image_uri_missing(card):
    if card['image_status'] == 'missing':
        return True
    else:
        return False


def lambda_handler(event, context):
    ttl = calculateTTL(ttlOffSetSecs, update_frequency_days)

    with requests.get("https://api.scryfall.com/bulk-data") as response:
        if response.status_code == 200:
            bulk_data_items = response.json()
        else:
            logger.info(f'Failed to fetch bulk data information. Status code: {response.status_code}')

    # Because we fetch a json file with multiple items with different types we first need to find the one with the type default_card
    for item in bulk_data_items["data"]:
        if item["type"] == "default_cards":
            default_cards_uri = item["download_uri"]
            break

    with requests.get(default_cards_uri, stream=True) as response:
        if response.status_code == 200:
            # wb for write bytes
            with open(local_filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logger.info(f"Downloaded '{local_filename}' successfully.")
        else:
            logger.info(f"Failed to download. Status code: {response.status_code}")
            return False

    with open(f'{local_filename}', "rb") as file:
        cards = ijson.items(file, 'item')

        item_list = []
        for card in cards:
            oracle_id = getOracleFromCard(card)
            card_info = createCardInfo(card, oracle_id)
            missing_image_uri = is_image_uri_missing(card)
            card_faces = []

            if card.get("card_faces") != None:
                face_count = 0
                for face in card['card_faces']:
                    if missing_image_uri:
                        card_image_uri = ''
                    else:
                        if get_image_uri_from_face(card):
                            card_image_uri = face['image_uris'].get('png', '')
                        else:
                            card_image_uri = card['image_uris'].get('png', '')

                    if get_Colors_from_face(card):
                        card_colors = face['colors']
                    else:
                        card_colors = card['colors']

                    face_count += 1
                    card_faces.append(turn_face_into_face_item(face, card_image_uri, card_colors))
            else:
                card_faces.append(turnCardIntoFaceItem(card))

            card_info['CardFaces'] = card_faces
            card_info['CombinedLowercaseOracleText'] = getCombinedLowerCaseOracleText(card_faces)
            item_list.append(card_info)
            item_list = cutTheListAndPersist(item_list, ttl)

        item_list = cutTheListAndPersist(item_list, ttl)

        if len(item_list) != 0:
            writeBatchToDb(item_list, table, ttl)

        logger.info("Finished!")
    return True
