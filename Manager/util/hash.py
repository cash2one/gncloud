import hashlib


#passowrd + salt => sha256
def random_string(password):
    base = str(password)
    hash = hashlib.sha256()
    hash.update(base+", "+"sha256")
    return hash.hexdigest()[:50]
