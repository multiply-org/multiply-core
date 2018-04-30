#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Prior Class for MULTIPLY.

    Copyright (C) 2018  Thomas Ramsauer
"""


import datetime
from dateutil.parser import parse
import numpy as np

__author__ = ["Alexander Löw", "Thomas Ramsauer"]
__copyright__ = "Copyright 2018, Thomas Ramsauer"
__credits__ = ["Alexander Löw", "Thomas Ramsauer"]
__license__ = "GPLv3"
__version__ = "0.0.1"
__maintainer__ = "Thomas Ramsauer"
__email__ = "t.ramsauer@iggf.geo.uni-muenchen.de"
__status__ = "Prototype"


class Prior(object):
    def __init__(self, **kwargs):
        self.ptype = kwargs.get('ptype', None)
        self.config = kwargs.get('config', None)
        self.datestr = kwargs.get('datestr', None)
        self.variable = kwargs.get('var', None)
        self._check()
        self._create_time_vector()
        self._create_month_id()

    def _check(self):
        assert self.ptype is not None, 'Invalid prior type'
        assert self.config is not None, 'No config available.'

    def _create_time_vector(self):
        """Creates a time vector dependent on start & end time and time interval
        from config file.
        A vector containing datetime objects is written to self.time_vector.
        A vector containing months ids (1-12) for each timestep is written to
        self.time_vector_months.

        :returns: -
        :rtype: -
        """
        date_format = ('%Y-%m-%d')
        s = self.config['General']['start_time']
        e = self.config['General']['end_time']
        interval = self.config['General']['time_interval']
        if type(s) is str:
            s = datetime.datetime.strptime(s, date_format)
        if type(e) is str:
            e = datetime.datetime.strptime(e, date_format)
        t_span = (e-s).days + 1
        # print(t_span)

        # create time vector

        self.time_vector = [(s+(datetime.timedelta(int(x))))
                            for x in np.arange(0, t_span, interval)]

        # create list of month ids for every queried point in time:
        idt_months = [(s+(datetime.timedelta(int(x)))).month
                      for x in np.arange(0, t_span, interval)]
        self.time_vector_months = idt_months

    def _create_month_id(self):
        # parse (dateutil) self.datestr to create datetime.datetime object
        try:
            self.date = parse(self.datestr)
        except TypeError as e:
            print('[WARNING] No time info was passed to Prior Class!')
            return
        # assert parsing of self.date is working.
        assert type(self.date) is datetime.datetime,\
            'could not parse date {}'.format(self.date)
            
        # get month id/number from self.datestr
        self.date_month_id = self.date.month

    def initialize(self):
        """Initialiszation routine. Should be implemented in child class.
        Prior calculation is initialized here.

        :returns: -
        :rtype: -

        """
        assert False, 'Should be implemented in child class'
