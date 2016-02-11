#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Generic linux daemon base class for python 3.x.
Copied from: http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
"""
import os
import sys
import time
import atexit
import signal
import subprocess


class Daemon:
    """A generic daemon class. Usage: subclass the daemon class and override 
    the run() method."""

    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""

        try:
            pid = os.fork()
            if pid > 0:
                # NOTE: Exit first parent!
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)

        # NOTE: Decouple from parent environment!
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # NOTE: Do second fork!
        try:
            pid = os.fork()
            if pid > 0:

                # NOTE: Exit from second parent!
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        # NOTE: Redirect standard file descriptors!
        os.setsid()

        sys.stdin.flush()
        sys.stdout.flush()
        sys.stderr.flush()

        null = os.open(os.devnull, os.O_RDWR)

        os.dup2(null, sys.stdin.fileno())
        os.dup2(null, sys.stdout.fileno())

        os.close(null)

        # NOTE: Write pidfile!
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile,'w+') as f:
            f.write(pid + '\n')

    def delpid(self):
        try:
            os.remove(self.pidfile)
        except FileNotFoundError as e:
            message = "%s" % e
            sys.stdout.write(message)

    def start(self):
        """Start the daemon."""

        # NOTE: Check for a pidfile to see if the daemon already 
        # runs!
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            if self.check_pid(pid):
                message = "pidfile {0} already exist. " + \
                        "Daemon already running?\n"
                sys.stderr.write(message.format(self.pidfile))
                sys.exit(1)
            else:
                self.delpid()

        self.killer(os.getpid())

        # NOTE: Start the daemon!
        try:
            self.daemonize()
            self.run()
        except PermissionError as e:
            message = "%s" % e
            sys.stderr.write(message)
            sys.exit(1)

    def stop(self):
        """Stop the daemon."""

        # NOTE: Get the pid from the pidfile!
        try:
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile {0} does not exist. " + \
                    "Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))

            # NOTE: Not an error in a restart!
            return

        self.killer(pid)

        # NOTE: Try killing the daemon process!
        try:
            while 1:
                os.killpg(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print (str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""

        self.stop()
        self.start()

    def check_pid(self, pid):
        """Check For the existence of a unix pid.
            @return bool
        """

        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def killer(self, ppid):
        """Kills all processes that are not descendants of the main corrent 
        process.
        """

        process = subprocess.Popen(
            ['ps', 'aux'],
            stdout=subprocess.PIPE,
            shell=False
        )
        out, err = process.communicate()
        for line in out.splitlines():
            if 'lbindex/ start' in line.decode('utf-8'):
                pid = int(line.split()[1])

                if not pid == ppid:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except OSError as e:
                        sys.stderr.write(str(s))

    def run(self):
        """You should override this method when you subclass Daemon.
        
        It will be called after the process has been daemonized by 
        start() or restart()."""
