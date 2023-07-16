import json
from functools import wraps
from urllib.request import urlopen

from flask import _request_ctx_stack, request, abort
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
ALGORITHMS = os.environ.get('ALGORITHMS')
API_AUDIENCE = os.environ.get('API_AUDIENCE')

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    # try/except block to use the flask abort function so the tests in Postman passes
    try:
        # if there is no header
        if not auth:
            raise AuthError('Authorization header is expected.', 401)

        # to check for the bearer and the token seperatly
        parts = auth.split()
        if parts[0].lower() != 'bearer':
            raise AuthError(
                'Authorization header must start with "Bearer".', 401)

        # if the lenght of the splited header is not 2 and
        # it passed the previous check then it doesn't have a token
        elif len(parts) == 1:
            raise AuthError('Token not found.', 401)

        # checks for the format of the header
        elif len(parts) > 2:
            raise AuthError('Authorization header must be Bearer<Token>.', 401)
    except:
        abort(401)

    token = parts[1]
    return token


'''
TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    # try/except block to use the flask abort function so the tests in Postman passes
    try:
        if 'permissions' not in payload:
            raise AuthError('Permissions not included in JWT.', 400)
    except:
        abort(400)

    try:
        if permission not in payload['permissions']:
            raise AuthError('Permission not found.', 403)
    except:
        abort(403)

    return True


'''
TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    # this is to compare with the provided token to make sure it is valid
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    # if there is no key id then it is an invalid header
    try:
        if 'kid' not in unverified_header:
            raise AuthError('Authorization malformed.', 401)
    except:
        abort(401)

    # does the compare to check that the key id matches the one provided
    # then it adds the values of the key(key type, key id, usage)
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # if rsa_key was not found it raises AuthError
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            try:
                raise AuthError('Token expired.', 401)
            except:
                abort(401)

        except jwt.JWTClaimsError:
            try:
                raise AuthError(
                    'Incorrect claims. Please, check the audience and issuer.', 401)
            except:
                abort(401)

        except Exception:
            try:
                raise AuthError('Unable to parse authentication token.', 400)
            except:
                abort(401)

    try:
        raise AuthError('Unable to find the appropriate key.', 400)
    except:
        abort(401)


'''
TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


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
