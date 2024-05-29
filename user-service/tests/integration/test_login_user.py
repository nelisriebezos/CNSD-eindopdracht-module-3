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

    signup_res = client.sign_up(
        ClientId=client_id,
        Username='maikel.reijneke@gmail.com',
        Password='NewPassword456!',
        UserAttributes=[
            {
                'Name': 'email',
                'Value': 'maikel.reijneke@gmail.com'
            }
        ]
    )

    client.admin_confirm_sign_up(
        UserPoolId=user_pool_id,
        Username='maikel.reijneke@gmail.com'
    )

    return client, user_pool_id, client_id


@mock_cognitoidp
def test_lambda_handler_successful():

    # Arrange
    client, user_pool_id, client_id = setup_mocks()

    event = {
        'body': json.dumps({
            'password': 'NewPassword456!',
            'email': 'maikel.reijneke@gmail.com'
        })
    }

    with patch.dict(os.environ, { 'USER_POOL_CLIENT_ID': client_id, 'USER_POOL_ID': user_pool_id }):

        from functions.login_user.app import lambda_handler

        # Act
        result = lambda_handler(event, {})

        # Assert
        assert result['statusCode'] == 200
        response_jwt_token = json.loads(result['body'])['token']
        assert response_jwt_token

@mock_cognitoidp
def test_lambda_handler_incorrect_password():

    # Arrange
    client, user_pool_id, client_id = setup_mocks()

    event = {
        'body': json.dumps({
            'password': 'WrongPassword456!',
            'email': 'maikel.reijneke@gmail.com'
        })
    }

    with patch.dict(os.environ, { 'USER_POOL_CLIENT_ID': client_id, 'USER_POOL_ID': user_pool_id }):

        from functions.login_user.app import lambda_handler

        # Act
        result = lambda_handler(event, {})

        # Assert
        assert result['statusCode'] == 403
        response_message = json.loads(result['body'])['error']
        assert response_message == 'Username or password is incorrect.'

@mock_cognitoidp
def test_lambda_handler_incorrect_email():

    # Arrange
    client, user_pool_id, client_id = setup_mocks()

    event = {
        'body': json.dumps({
            'password': 'NewPassword456!',
            'email': 'wrong@gmail.com'
        })
    }

    with patch.dict(os.environ, { 'USER_POOL_CLIENT_ID': client_id, 'USER_POOL_ID': user_pool_id }):

        from functions.login_user.app import lambda_handler

        # Act
        result = lambda_handler(event, {})

        # Assert
        assert result['statusCode'] == 403
        response_message = json.loads(result['body'])['error']
        assert response_message == 'Username or password is incorrect.'

@mock_cognitoidp
def test_lambda_handler_unconfirmed_account():

    # Arrange
    client, user_pool_id, client_id = setup_mocks()

    unconfirmed_signup_res = client.sign_up(
        ClientId=client_id,
        Username='maikel.reijneke+1@gmail.com',
        Password='NewPassword456!2',
        UserAttributes=[
            {
                'Name': 'email',
                'Value': 'maikel.reijneke+1@gmail.com'
            }
        ]
    )

    event = {
        'body': json.dumps({
            'password': 'NewPassword456!2',
            'email': 'maikel.reijneke+1@gmail.com'
        })
    }

    with patch.dict(os.environ, { 'USER_POOL_CLIENT_ID': client_id, 'USER_POOL_ID': user_pool_id }):

        from functions.login_user.app import lambda_handler

        # Act
        result = lambda_handler(event, {})

        # Assert
        assert result['statusCode'] == 400
        response_message = json.loads(result['body'])['error']
        assert response_message == 'User is not confirmed yet. Please check your email.'
