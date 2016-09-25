# -*- coding: utf-8 -*-
# Shamelessly adapted from http://stackoverflow.com/questions/2281850/

import signal


class timeout(object):

    """Times out after a given number of seconds.

    Usage:
        >>>    with timeout(seconds):
        ...        # something slow...
        TimeoutError
    """

    def __init__(self, seconds):
        """Creates a timeout after a number of seconds.

        Args:
            seconds: Number of seconds until timeout.
        """
        self.seconds = seconds

    def handle_timeout(self, signum, frame):
        """Handles timeout signal.

        Args:
            signum: Signal number.
            frame: Frame.
        """
        raise TimeoutError

    def __enter__(self):
        """Handles entering on with statement."""
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        """Handles exit of with statement and cancels timeout."""
        signal.alarm(0)
