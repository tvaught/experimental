#!/usr/bin/env python
# encoding: utf-8
"""
mpt.py

Created by Travis Vaught on 2011-08-13.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD
"""

# Standard library imports ####
import datetime
import logging
import copy

# Library imports ####
import numpy as np
import sqlite3

# Local imports ####
from metrics import (annualized_adjusted_rate, beta_bb, 
    expected_return, rate_array, TRADING_DAYS_PER_YEAR)
    
import price_utils

# Constants ####
price_schema = np.dtype({'names':['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'adj_close'], 'formats':['S8', long, float, float, float, float, float, float]})


class Stock(object):
    
    def __init__(self, symbol, startdate="1995-1-1",
        enddate="2011-7-31", dbfilename='data/stocks.db', bench='^GSPC', rfr=0.015):
        self.symbol = symbol
        self.startdate = startdate
        self.enddate = enddate
        self.rfr = rfr
        
        #self.conn = sqlite3.connect(db)
        
        self.bench_data = price_utils.load_from_db(bench, 
                                        self.startdate,
                                        self.enddate,
                                        dbfilename=dbfilename)
        self.stock_data = price_utils.load_from_db(symbol,
                                        self.startdate,
                                        self.enddate,
                                        dbfilename=dbfilename)

        if len(self.bench_data)!=len(self.stock_data):
            print("Full Stock data not available: needs imputation")
        self.update_metrics()
        
        
    def update_metrics(self):
        self.ratearray = rate_array(self.stock_data)
        self.bencharray = rate_array(self.bench_data)
        # TODO: Not sure if these are the metrics I'm looking for...
        #self.annual_volatility = self.ratearray["rate"].std()**2
        #print self.ratearray[-1], self.bencharray[-1]
        self.beta = beta_bb(self.ratearray, self.bencharray)
        self.annualized_adjusted_return = annualized_adjusted_rate(self.ratearray, rfr=0.01)
        self.expected_return = expected_return(self.ratearray,
                                               self.bencharray,
                                               rfr=self.rfr)
        