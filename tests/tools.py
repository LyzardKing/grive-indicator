#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from contextlib import suppress
import signal
import pexpect
from time import sleep


EXEC = './bin/grive-indicator'


def _pid_for(process_grep):
        """Return pid matching the process_grep elements"""
        for pid in os.listdir('/proc'):
            if not pid.isdigit():
                continue
            # ignore processes that are closed in between
            with suppress(IOError):
                cmdline = open(os.path.join('/proc', pid, 'cmdline'), 'r').read()
                for process_elem in process_grep:
                    if process_elem not in cmdline:
                        break
                # we found it
                else:
                    return int(pid)
        raise BaseException("The process that we can find with {} isn't started".format(process_grep))


def check_and_kill_process(process_grep, wait_before=0, send_sigkill=False):
    """Check a process matching process_grep exists and kill it"""
    sleep(wait_before)
    pid = _pid_for(process_grep)
    if send_sigkill:
        os.killpg(pid, signal.SIGKILL)


def spawn_process(command):
    """return a handle to a new controllable child process"""
    return pexpect.spawnu(command, dimensions=(24, 250))


def set_env(system):
    global EXEC
    if system:
        print('Using system version for tests')
        EXEC = 'grive-indicator'
