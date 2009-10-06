#!/usr/bin/env python
# encoding: utf-8
"""
portfolio_test.py

Created by Travis Vaught on 2009-09-30.
Copyright (c) 2009 Vaught Consulting. All rights reserved.

License: BSD

"""

# Local imports
import position
import portfolio

def portfolio_holding_test():
    """ Simple test to add position to holdings. """

    p = position.Position(symbol="AAPL", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
                          
    h = portfolio.Holding()
    
    h.add_to(p)
    
    assert h.qty==1000
    
    return
    
def portfolio_holding_fifo_test():
    """ test of 'fifo' and 'lifo' queuing by adding and removing
        a position.
        Note: there are no protections on 'removing' a position which
              is in the wrong direction.  ## TODO: decide when to make
              determination of add or remove -- in the class or when
              deciding to call the appropriate method?
    """
    p1 = position.Position(symbol="AAPL", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", qty=1500, price=184.00,
                          multiplier=1., fee=7.0, total_amt=276000.,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="AAPL", qty=-1500, price=186.00,
                          multiplier=1., fee=7.0, total_amt=279000.,
                          trans_date=1055902486.22)
                          
    h = portfolio.Holding()
    
    h.add_to(p1)
    h.add_to(p2)
    
    h.remove_from(p3, order='fifo')
    
    assert h.qty==1000
    assert len(h.positions)==1
    # simple check to make sure the position that we expect is left over...
    p = h.positions[0]
    assert p.price==184.00
    
def portfolio_holding_fifo2_test():
    """ test of 'fifo' and 'lifo' queuing by adding and removing
        a position.
        Note: there are no protections on 'removing' a position which
              is in the wrong direction.  ## TODO: decide when to make
              determination of add or remove -- in the class or when
              deciding to call the appropriate method?
    """
    p1 = position.Position(symbol="AAPL", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", qty=1500, price=184.00,
                          multiplier=1., fee=7.0, total_amt=276000.,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="AAPL", qty=-500, price=186.00,
                          multiplier=1., fee=7.0, total_amt=279000.,
                          trans_date=1055902486.22)
                          
    h = portfolio.Holding()
    
    h.add_to(p1)
    h.add_to(p2)
    
    h.remove_from(p3, order='fifo')
    
    assert h.qty==2000
    assert len(h.positions)==2
    # simple check to make sure the positions that we expect are left over...
    p = h.positions[0]
    assert p.price==185.25
    p = h.positions[1]
    assert p.price==184.00
    
def portfolio_holding_lifo_test():
    """ test of 'lifo' queuing by adding and removing
        a position.
    """
    p1 = position.Position(symbol="AAPL", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", qty=1500, price=184.00,
                          multiplier=1., fee=7.0, total_amt=276000.,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="AAPL", qty=-1500, price=186.00,
                          multiplier=1., fee=7.0, total_amt=279000.,
                          trans_date=1055902486.22)
                          
    h = portfolio.Holding()
    
    h.add_to(p1)
    h.add_to(p2)
    
    h.remove_from(p3, order='lifo')
    
    print "Holding: ", h
    print "Positions length: ", len(h.positions)
    print "Positions price: ", h.positions[0].price, h.positions[0].fee
    assert h.qty==1000
    assert len(h.positions)==1
    # simple check to make sure the position that we expect is left over...
    p = h.positions[0]
    assert p.price==185.25

def portfolio_holding_lifo2_test():
    """ test of 'lifo' queuing by adding and removing
        a position.
    """
    p1 = position.Position(symbol="AAPL", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", qty=1500, price=184.00,
                          multiplier=1., fee=7.0, total_amt=276000.,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="AAPL", qty=-2000, price=186.00,
                          multiplier=1., fee=7.0, total_amt=279000.,
                          trans_date=1055902486.22)
                          
    h = portfolio.Holding()
    
    h.add_to(p1)
    h.add_to(p2)
    
    h.remove_from(p3, order='lifo')
    
    print "Holding: ", h
    print "Positions length: ", len(h.positions)
    print "Positions price: ", h.positions[0].price, h.positions[0].fee
    assert h.qty==500
    assert len(h.positions)==1
    # simple check to make sure the position that we expect is left over...
    p = h.positions[0]
    assert p.price==185.25
    
    
#### EOF ####################################################################