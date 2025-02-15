import time
from jose import jwt


def generate_test_jwt(user_id='test-user', secret_key='secret', algorithm='HS256', claims=None):
    if claims is None:
        claims = {}

    # Set default claims (you can customize these as needed)
    default_claims = {
        'iss': 'test_issuer',
        'sub': user_id,
        'aud': 'test_audience',
        'exp': int(time.time()) + 3600,  # Expiration time (1 hour)
        'iat': int(time.time()),  # Issued at
        'cognito:username': user_id
    }

    # Merge default and user-provided claims
    all_claims = {**default_claims, **claims}

    # Generate JWT
    token = jwt.encode(all_claims, secret_key, algorithm=algorithm)

    return token
