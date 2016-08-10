from __future__ import absolute_import,unicode_literals

import os
import socket
import logging
import threading

from synapse.exc import *

logger = logging.getLogger(__name__)

def setProcName(name):
    '''
    Set the process title/name for process listing.
    '''
    logger.info('setProcName: %s' % (name,))

def getVolInfo(*paths):
    '''
    Retrieve volume usage info for the given path.
    '''
    path = os.path.join(*paths)
    path = os.path.expanduser(path)

    st = os.statvfs(path)

    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize

    return {
        'free':free,
        'used':total - free,
        'total':total,
    }

def inet_pton(afam,text):
    return socket.inet_pton(afam,text)

def inet_ntop(afam,byts):
    return socket.inet_ntop(afam,byts)

def daemonize():
    '''
    For unix platforms, form a new process group using fork().
    '''
    if os.fork() != 0:
        exit()

    if os.fork() != 0:
        exit()

def initHostInfo():
    return {}
