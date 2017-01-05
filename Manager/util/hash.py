import hashlib

import datetime


#passowrd + salt => sha256
def random_string(password):
    base = str(password)
    hash = hashlib.sha256()
    hash.update(base+", "+"sha256")
    return hash.hexdigest()[:50]

def delcode(number):
    base = str(datetime.datetime.now())
    hash = hashlib.sha256()
    hash.update(base+", "+"sha256")
    return hash.hexdigest()[:number]
