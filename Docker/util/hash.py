import hashlib
import uuid
import datetime
import string
import random



#datetime + salt => sha256
def random_string(salt, number):
    base = str(datetime.datetime.now())
    #print "base: {0} salt: {1}".format(base, salt)
    msg = base+", "+salt
    #print msg
    hash = hashlib.sha256()
    hash.update(base+", "+salt)

    return hash.hexdigest()[:number]

# #upper/lower/number => random chice
# def random_string2(length):
#     pool = string.letters + string.digits
#     print pool
#     return ''.join(random.choice(pool) for i in xrange(length))

#uuid+salt => sha256
# def random_string3(salt, number):
#     base = str(uuid.uuid4().get_hex())
#     print "base: {0} salt: {1}".format(base, salt)
#     msg = base+", "+salt
#     print msg
#     hash = hashlib.sha256()
#     hash.update(base+", "+salt)
#
#     return hash.hexdigest()[:number]

# if __name__ == "__main__":
#     salt = "test"
#     for i in range(100):
#         print(random_string(salt,8))