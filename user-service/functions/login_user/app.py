import json
import os

import boto3
from botocore.exceptions import ClientError
from aws_xray_sdk.core import patch_all
import logging

patch_all()

logger = logging.getLogger()
logger.setLevel("INFO")

client = boto3.client('cognito-idp', region_name='us-east-1')


def lambda_handler(event, context):

    client_id = os.environ['USER_POOL_CLIENT_ID']

    logger.info(f'EventType: {type(event)}')
    logger.info(f'Event: {event}')

    logger.info(f'Client: {client}')
    logger.info(f'ClientID: {client_id}')

    body = json.loads(event['body'])
    password = body['password']
    email = body['email']


    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )        
        id_token = response['AuthenticationResult']['IdToken']
        logger.info(response)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'token': id_token
            })
        }
    except ClientError as e:
        logger.error(e.response)

        if e.response['Error']['Code'] == 'NotAuthorizedException' or e.response['Error']['Code'] == 'UserNotFoundException':
            return {
                'statusCode': 403,
                "body": json.dumps({
                    "error": "Username or password is incorrect."
                })
            }
        elif e.response['Error']['Code'] == 'UserNotConfirmedException':
            return {
                'statusCode': 400,
                "body": json.dumps({
                    "error": "User is not confirmed yet. Please check your email."
                })
            }

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Something went wrong.'
            })
        }