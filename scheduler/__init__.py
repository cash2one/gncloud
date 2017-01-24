# -*- coding: utf-8 -*-
__author__ = 'nhcho'

import daemon
from daemon.pidfile import PIDLockFile
from util.logger import file_handler
from controller.scheduler import ScheduleController

pidLockfile = PIDLockFile('.pid')
if pidLockfile.is_locked():
    print "running already (pid: %d)" % pidLockfile.read_pid()
    exit(1)

context = daemon.DaemonContext(pidfile=pidLockfile)
logfile_fileno = file_handler.stream.fileno()
context.files_preserve = [logfile_fileno]

app=ScheduleController()

if __name__ == '__main__':
    app.run()

