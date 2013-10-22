from uuid import uuid4
import hmac
from hashlib import sha1

# Based on code from Beaker

def generate_id():
    return str(uuid4()).replace('-', '')

def generate_secure_id(secret):
    sid = generate_id()
    sig = hmac.new(secret, sid.encode('utf-8'), sha1).hexdigest()
    return '%s%s' % (sig, sid)

def get_secure_id(secret, val):
    val = val.strip('"')
    sig = hmac.new(secret, val[40:].encode('UTF-8'), sha1).hexdigest()

    # Avoid timing attacks
    invalid_bits = 0
    input_sig = val[:40]
    if len(sig) != len(input_sig):
        return None

    for a, b in zip(sig, input_sig):
        invalid_bits += a != b

    if invalid_bits:
        return None
    else:
        return val[40:]

