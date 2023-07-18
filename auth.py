from flask import request, abort
from functools import wraps
import json
import os
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

KEY = os.getenv("SECRET_KEY")
KEY = KEY.encode('latin-1')
url_safe_key = base64.urlsafe_b64encode(KEY)
f = Fernet(url_safe_key)

def generate_token(**user):
    #name, role, permissions

    user_byte = json.dumps(user).encode('utf-8')
    # user = json.loads(user_byte).decode('utf-8)    
    token = f.encrypt(user_byte)
    return token


def load_token(token):
    data = f.decrypt(token.encode('utf-8'))
    user = data.decode('utf-8')
    user = json.loads(user)

    if 'name' not in user:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401
        )
    
    if 'role' not in user:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401
        )
    
    if 'permission' not in user:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401
        )
    
    return user



def get_token_auth_header():
    # get the access token from authorization header
    authorization = request.headers.get('Authorization', None)
    
    if authorization is None:
        raise AuthError(
            {
                'code': 'authorization_header_missing',
                'description': 'Authorization header is required'
            }, 401
        )

    splits = authorization.split()

    if splits[0].lower() != 'bearer':
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization header must start with "Bearer".'
            }, 401
        )

    elif len(splits) == 1:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Token not found'
            }, 401
        )

    elif len(splits) > 2:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization header must be Bearer token'
            }, 401
        )

    token = splits[1]
    return token

def check_permissions(permission, user):
    if 'permission' not in user:
        raise AuthError(
            {
                'code': 'invalid_claims',
                'description': 'Permission not included in token'
            }, 400
        )

    if permission not in user['permission']:
        raise AuthError(
            {
                'code': 'unauthorized',
                'description': 'Permission not found'
            }, 403
        )

    return True


def decode_token(token):
    try:
        user = load_token(token)
        return user
    except:
        raise AuthError(
        {
            'code': 'invalid_header',
            'description': 'Unable to decode token.'
        }, 400
    )


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                user = decode_token(token)
            except:
                abort(401)

            check_permissions(permission, user)

            return f(user, *args, **kwargs)

        return wrapper
    return requires_auth_decorator