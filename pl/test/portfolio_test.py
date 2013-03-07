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

    p = position.Position(symbol="AAPL", id="1234", qty=1000, price=185.25,
                          total_amt=185250., fee=7.00,
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
    p1 = position.Position(symbol="AAPL", id="1235", qty=1000, price=185.25,
                          total_amt=185250., fee=7.0,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", id="1236", qty=1500, price=184.00,
                          total_amt=276000., fee=7.0,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="AAPL", id="1237", qty=-1500, price=186.00,
                          total_amt=279000., fee=7.0,
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
    p1 = position.Position(symbol="AAPL", id="1238", qty=1000, price=185.25,
                          fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", id="1239", qty=1500, price=184.00,
                          fee=7.0, total_amt=276000.,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="AAPL", id="1240", qty=-500, price=186.00,
                          fee=7.0, total_amt=279000.,
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
    p1 = position.Position(symbol="AAPL", id="1241", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", id="1242", qty=1500, price=184.00,
                          multiplier=1., fee=7.0, total_amt=276000.,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="AAPL", id="1243", qty=-1500, price=186.00,
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
    p1 = position.Position(symbol="AAPL", id="1110", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", id="1111", qty=1500, price=184.00,
                          multiplier=1., fee=7.0, total_amt=276000.,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="AAPL", id="1112", qty=-2000, price=186.00,
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
    

def portfolio_port_test():
    """ test of 'lifo' queuing by adding and removing
        a position.
    """
    p1 = position.Position(symbol="AAPL", id="1110", qty=1000, price=185.25,
                          multiplier=1., fee=7.0, total_amt=185250.,
                          trans_date=1053605468.54)
    p2 = position.Position(symbol="AAPL", id="1111", qty=1500, price=184.00,
                          multiplier=1., fee=7.0, total_amt=276000.,
                          trans_date=1054202245.63)
    p3 = position.Position(symbol="GOOG", id="1112", qty=2000, price=286.00,
                          multiplier=1., fee=7.0, total_amt=572000.,
                          trans_date=1055902486.22)

    h = portfolio.Holding()

    h.add_to(p1)
    h.add_to(p2)

    h2 = portfolio.Holding()
    h2.add_to(p3)
    
    portf = portfolio.Portfolio(name="Test Portfolio", holdings=[h,h2])

    print dir(portf)
    print portf.holdings
    print portf.pprint
    assert len(portf.holdings)==2
    assert portf.holdings["GOOG"].symbol=="GOOG"

    return

#### EOF ####################################################################
