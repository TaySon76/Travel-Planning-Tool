import jwt
import uuid
import base64
import datetime
import secrets
from .secrets import secret_key

key = secret_key

def generate_shareable_link():
    unique_id = str(uuid.uuid4())
    payload = {
        'uuid': unique_id,
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return token


