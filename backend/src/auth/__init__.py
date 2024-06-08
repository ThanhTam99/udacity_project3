import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import re


AUTH0_DOMAIN = 'dev-gjnagefq5ixxakc.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://coffee-shop.com'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header
def get_token_auth_header():
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        raise AuthError('Token does not provided', 401)
    match = re.match("(Bearer) ([\w-]+\.[\w-]+.[\w-]+)$", auth_header)
    if match is None:
        raise AuthError('Invalid header format', 401)
    return match.group(2)
    


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({"code": "invalid_claims", "description":
                         "Permissions not included in JWT."}, 400)
    if permission not in payload['permissions']:
        raise AuthError({"code": "unauthorized", "description":
                         "Permission not found."}, 403)
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({"code": "invalid_header", "description": "Authorization malformed."}, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired", "description": "Token expired."}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims", "description":
                             "Incorrect claims. Please, check the audience and issuer."}, 401)
        except Exception:
            raise AuthError({"code": "invalid_token", "description":
                             "Invalid token."}, 401)
    raise AuthError({"code": "invalid_header", "description": "Unable to find appropriate key."}, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator