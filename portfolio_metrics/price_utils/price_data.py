#!/usr/bin/env python
# encoding: utf-8
"""
price_data.py

Created by Travis Vaught on 2011-08-24.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD
"""

# Standard library imports
import datetime, time
from urllib import urlopen

# Major library imports
import numpy as np

# Constants
schema = np.dtype({'names':['symbol', 'date', 'open', 'high', 'low',
                       'close', 'volume', 'adjclose'],
                   'formats':['S8', 'M8[D]', float, float, float, float,
                       float, float]})

def get_yahoo_prices(symbol, startdate=None, enddate=None,
                     period='d', datefmt="%Y-%m-%d"):
    """ Utility function to pull price data from Yahoo Finance site.
    
        Parameters:
        symbol: string, a valid financial instrument symbol
        startdate: string, a date string representing the beginning date
            for the requested data.
        enddate: string, a date string representing the ending date for the 
            requested data.
        period: string {'d', 'w', 'y'}, representing the period of data
            requested.
        datefmt: string, a date format string designating the format for
            the startdate and enddate input parameters.
        
        Returns:
        numpy array containing dates and price/volume data in the following
        dtype:
        numpy.dtype({'names':['symbol', 'date', 'open', 'high', 'low',
                              'close', 'volume', 'adjclose'],
                     'formats':['S8', 'M8[D]', float, float, float, float,
                                float, float]})
    """
    
    todaydate = datetime.date(*time.localtime()[:3])
    yesterdate = todaydate - datetime.timedelta(1)
    lastyeardate = todaydate - datetime.timedelta(365)
    
    if startdate is None:
        startdate = lastyeardate
    else:
        startdate = datetime.datetime.strptime(startdate, datefmt)
    
    if enddate is None:
        enddate = yesterdate
    else:
        enddate = datetime.datetime.strptime(enddate, datefmt)
    
    # Note: account for Yahoo's messed up 0-indexed months
    url = "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%d&b=%d&c=%d&"\
              "d=%d&e=%d&f=%d&y=0&g=%s&ignore=.csv" % (symbol,
              startdate.month-1, startdate.day, startdate.year,
              enddate.month-1, enddate.day, enddate.year, period)
    
    filehandle = urlopen(url)
    lines = filehandle.readlines()
    
    data = []
    
    for line in lines[1:]:
        
        items = line.strip().split(',')
        
        if len(items)!=7:
            # skip bad data for now
            continue
        
        dt = items[0]
        opn, high, low, close, volume, adjclose = [float(x) for x in items[1:7]]
        data.append((symbol, dt, opn, high, low, close, volume, adjclose))
    
    npdata = np.array(data, dtype=schema)
    
    return npdata
        
    
def get_yahoo_dividends(symbol, startdate, enddate, datefmt="%Y-%m-%d"):

    """ Utility function to pull dividend data from Yahoo Finance site.
    
        Parameters:
        symbol: string, a valid financial instrument symbol
        startdate: string, a date string representing the beginning date
            for the requested data.
        enddate: string, a date string representing the ending date for the 
            requested data.
        datefmt: string, a date format string designating the format for
            the startdate and enddate input parameters.
    
        Returns:
        numpy array containing dates and price/volume data in the following
        dtype:
        numpy.dtype({'names':['symbol', 'date', 'dividend'],
                     'formats':['S8', 'M8[D]', float]})
        TODO: Not Implemented yet.
    """
    
    raise NotImplementedError
    
if __name__ == '__main__':
	main()

