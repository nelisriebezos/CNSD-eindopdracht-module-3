import json
import os
import boto3
from botocore.exceptions import ClientError
from moto import mock_cognitoidp
from unittest.mock import patch


def setup_mocks():
    client = boto3.client('cognito-idp', region_name='us-east-1')

    pool_res = client.create_user_pool(
        PoolName='TestUserPool',
        AutoVerifiedAttributes=['email']
    )
    user_pool_id = pool_res['UserPool']['Id']

    client_res = client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName='TestUserPoolClient',
        GenerateSecret=False
    )
    client_id = client_res['UserPoolClient']['ClientId']

    event = {
        'body': json.dumps({
            'password': 'NewPassword456!',
            'email': 'maikel.reijneke@gmail.com'
        })
    }

    return client, user_pool_id, client_id, event


@mock_cognitoidp
def test_lambda_handler_successful():

    # Arrange
    client, user_pool_id, client_id, event = setup_mocks()

    with patch.dict(os.environ, { 'USER_POOL_CLIENT_ID': client_id, 'USER_POOL_ID': user_pool_id }):

        from functions.register_user.app import lambda_handler

        # Act
        result = lambda_handler(event, {})


        # Assert
        assert result['statusCode'] == 201
        response_user = client.admin_get_user(
                UserPoolId=user_pool_id,
                Username='maikel.reijneke@gmail.com'
            )
        assert response_user


@mock_cognitoidp
def test_lambda_handler_email_exists():

    # Arrange
    client, user_pool_id, client_id, event = setup_mocks()

    client.admin_create_user(
        UserPoolId=user_pool_id,
        Username='maikel.reijneke@gmail.com',
        TemporaryPassword='NewPassword456!',
        UserAttributes=[
            {
                'Name': 'email',
                'Value': 'maikel.reijneke@gmail.com'
            }
        ]
    )
    
    with patch.dict(os.environ, { 'USER_POOL_CLIENT_ID': client_id,'USER_POOL_ID': user_pool_id }):

        from functions.register_user.app import lambda_handler

        # Act
        result = lambda_handler(event, {})

        # Assert
        assert result['statusCode'] == 409
        response_body = json.loads(result['body'])
        assert response_body['error'] == 'Email address is already in use.'
        

@mock_cognitoidp
def test_lambda_handler_password_too_short():

    # Arrange
    client, user_pool_id, client_id, event = setup_mocks()

    event = {
        'body': json.dumps({
            'password': 'Pass',
            'email': 'maikel.reijneke@gmail.com'
        })
    }

    with patch.dict(os.environ, { 'USER_POOL_CLIENT_ID': client_id, 'USER_POOL_ID': user_pool_id }):

        from functions.register_user.app import lambda_handler

        # Act
        result = lambda_handler(event, {})

        # Assert
        assert result['statusCode'] == 400
        response_body = json.loads(result['body'])
        assert response_body['error'] == 'Password must be at least 8 characters long.'