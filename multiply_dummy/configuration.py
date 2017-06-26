"""
module for MULTIPLY platfrom configuration
"""

import datetime

class Configuration(object):
    def __init__(self, **kwargs):
        self.region = kwargs.get('region', None)

        self.time_start = kwargs.get('time_start', None)
        self.time_stop = kwargs.get('time_stop', None)

        self._check()

    def _check(self):
        assert self.region is not None, 'ERROR: region needs to be specified'
        assert self.time_start is not None
        assert self.time_stop is not None
        assert isinstance(self.time_start, datetime.datetime)
        assert isinstance(self.time_stop, datetime.datetime)
