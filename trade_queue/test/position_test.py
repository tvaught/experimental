#!/usr/bin/env python
# encoding: utf-8
"""
position_test.py

Created by Travis Vaught on 2009-09-29.
Copyright (c) 2009 Vaught Consulting. All rights reserved.

License: BSD

"""


import position

def position_attribute_test():
    """ Dead simple test to see if I can store data in my position object
        and get it back out
    """
    p = position.Position(symbol="AAPL", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
                          
    assert p.price==185.25


def position_initialization_test():
    """ Test to see if I can handle fields for which I provide no data.
    """
    p = position.Position(symbol="AAPL", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    
    
    assert p.description==""


def position_dates_test():
    """ Test to see if I'm handling dates correctly
    """
    p = position.Position(symbol="AAPL", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    
    assert p.date_display=="05/22/2003"
    assert p.time_display=="08:11:08"


def position_sort_test():
    """ Test to see if I can collect and sort these properly.
        The objective is to have the objects sort by the trans_date
        trait.
    """
    
    
    p0 = position.Position(id=102, symbol="AAPL", qty=1000, price=185.25,
                           multiplier=1., fee=7.0, total_amt=185250.,
                           trans_date=1045623459.68)
    
    p1 = position.Position(id=103, symbol="AAPL", qty=-1000, price=186.25,
                           multiplier=1., fee=7.0, total_amt=-186250.,
                           trans_date=1053605468.54)
    
    p2 = position.Position(id=101, symbol="AAPL", qty=500, price=184.00,
                           multiplier=1., fee=7.0, total_amt=62000.,
                           trans_date=1021236990.02)
    
    plist = [p0, p1, p2]
    
    plist.sort()
    
    assert plist[0]==p2
    assert plist[1]==p0
    assert plist[2]==p1
    
    
    
#### EOF ####################################################################