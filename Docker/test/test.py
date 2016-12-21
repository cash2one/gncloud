__author__ = 'jhjeon'

# from pexpect import pxssh
#
# s = pxssh.pxssh()
#
# if not s.login('192.168.0.20', 'docker', 'docker'):
#     # print "SSH session failed on login."
#     print str(s)
# else:
#     # print "SSH session login successful"
#     s.sendline("docker inspect --format='{{json .Config}}' mariadb:latest")
#     s.prompt()
#     json = s.before.split("\r\n", 2)[1]
#     error = s.before.split("\r\n", 2)[2]
#     print "json value: %s" % json
#     print "error msg: %s" % error
#     s.logout()

# '''time date format test'''
# import datetime
#
# timestr = "2016-12-15T11:58:27.5428889Z"
# time = datetime.datetime.strptime(timestr[:-2], "%Y-%m-%dT%H:%M:%S.%f")
# print time
