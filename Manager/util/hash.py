import hashlib

import datetime


#datetime + salt => sha256
def random_string(number):
    base = str(datetime.datetime.now())
    hash = hashlib.sha256()
    hash.update(base+", "+"sha256")
    return hash.hexdigest()[:number]

#passowrd + salt => sha256
def convertToHashValue(password):
    base = str(password)
    hash = hashlib.sha256()
    hash.update(base+", "+"sha256")
    return hash.hexdigest()[:50]

def convertsize(size):
    size_re=size.upper()
    size_split = size_re.partition('GB')
    if(size_split[1] ==""):
        size_split = size_re.partition('TB')
        if(size_split[1] ==""):
           size_split=size_re.partition('MB')
           if(size_split[1] ==""):
                size_split=size_re.partition('B')
                size_split[0].strip()
                return int(size_split[0])
           size_split[0].strip()
           return int(size_split[0])*1024**2
        size_split[0].strip()
        return int(size_split[0])*1024**4
    else:
        size_split[0].strip()
        return int(size_split[0])*1024**3
