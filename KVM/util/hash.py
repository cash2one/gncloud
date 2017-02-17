import hashlib
import uuid
import datetime
import string
import random

#datetime + salt => sha256
def random_string(number):
    base = str(datetime.datetime.now())
    hash = hashlib.sha256()
    hash.update(base+", "+"sha256")
    return hash.hexdigest()[:number]
