import hashlib
import datetime

def random_string(salt, number):
    base = str(datetime.datetime.now())
    hash = hashlib.sha256()
    hash.update(base+", "+salt)
    return hash.hexdigest()[:number]