#!/usr/bin/env python
# encoding: utf-8
"""
position.py

Created by Travis Vaught on 2009-09-21.
Copyright (c) 2009 Vaught Consulting. All rights reserved.

License: BSD

"""

# Standard library imports
from datetime import datetime

# Enthought library imports
from enthought.traits.api import (HasTraits, Enum, Float, Int,
                                  Property, Regex, Str)
from enthought.traits.ui.api import Item, View

# Local library imports
from date_util import dt_to_timestamp, dt_from_timestamp, Eastern


class Position(HasTraits):
    """ Simple object to act as a data structure for a position 
    
        While all attributes (traits) are optional, classes that contain or
        collect instances of the Position class will require the following:
        symbol, trans_date, qty, price, total_amt
    
    """
    
    
    side = Enum("BUYTOOPEN", ["SELLTOCLOS", "BUYTOOPEN", "SELLTOOPEN", "BUYTOCLOSE"])
    symbol = Str
    id = Int
    description = Str
    trans_date = Float
    qty = Float
    price = Float
    multiplier = Float(1.0)
    fee = Float
    exchange_rate = Float(1.0)
    currency = Str("USD")
    total_amt = Float
    filled = Str
    exchange = Str
    
    # The following traits are for viewing and editing the datetime value
    #     of trans_date (which is a float of seconds since the Epoch)
    date_display = Property(Regex(value='11/17/1969',
                                  regex='\d\d[/]\d\d[/]\d\d\d\d'),
                                  depends_on='trans_date')
    time_display = Property(Regex(value='12:01:01',
                                  regex='\d\d[:]\d\d[:]\d\d'),
                                  depends_on='trans_date')
    
    # specify default view layout
    traits_view = View(Item('symbol', label="Symb"),
                       Item('date_display'),
                       Item('time_display'),
                       Item('qty'),
                       buttons=['OK', 'Cancel'], resizable=True)
    
    ###################################
    # Property methods
    def _get_date_display(self):
        return dt_from_timestamp(self.trans_date, tz=Eastern).strftime("%m/%d/%Y")
        
    def _set_date_display(self, val):
        tm = self._get_time_display()
        trans_date = datetime.strptime(val+tm, "%m/%d/%Y%H:%M:%S" )
        trans_date = trans_date.replace(tzinfo=Eastern)
        self.trans_date = dt_to_timestamp(trans_date)
        return 
        
    def _get_time_display(self):
        t = dt_from_timestamp(self.trans_date, tz=Eastern).strftime("%H:%M:%S")
        return t
        
    def _set_time_display(self, val):
        trans_time = datetime.strptime(self._get_date_display()+val, "%m/%d/%Y%H:%M:%S")
        trans_time = trans_time.replace(tzinfo=Eastern)
        self.trans_date = dt_to_timestamp(trans_time)
        return

    ###################################
    # Override default class methods
    
    # cleaner, more reasonable representation of the object
    def __repr__(self):
        return "<Position %s %s>" % (self.symbol, self.qty)
    
    # support reasonable sorting based on trans_date
    def __cmp__(self, other):
        if self.trans_date < other.trans_date:
            return -1
        elif self.trans_date > other.trans_date:
            return 1
        else: return 0

#### EOF ####################################################################