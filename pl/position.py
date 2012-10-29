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

# Major package imports
import pandas

# Local library imports
from date_util import dt_to_timestamp, dt_from_timestamp, Eastern


class Position():
    """ Simple object to act as a data structure for a position 
    
        While all attributes are optional, classes that contain or
        collect instances of the Position class will require the following:
        symbol, trans_date, qty, price, total_amt
    
    """
    
    def __init__(self, symbol, id, trans_date, qty, price, description="",
                    side="BUY", multiplier=1.0, fee=0.0, exchange_rate=1.0,
                    currency="USD", total_amt=0.0, filled=True, exchange=""):
        
        self.side = side
        self.symbol = symbol
        self.id = id
        self.description = description
        self.trans_date = trans_date
        self.qty = qty
        self.price = price
        self.multiplier = multiplier
        self.fee = fee
        self.exchange_rate = exchange_rate
        self.currency = currency
        self.total_amt = total_amt
    
    ################################
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