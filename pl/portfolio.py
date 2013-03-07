#!/usr/bin/env python
# encoding: utf-8
"""
portfolio.py

Created by Travis Vaught on 2009-10-03.
Copyright (c) 2009 Vaught Consulting. All rights reserved.

License: BSD

"""

# Major package imports
import pandas

# Local imports
from position import Position

class Portfolio():
    """ Dead simple container for Holdings """
    
    def __init__(self, name="", holdings=None, cash_bal=0.0):
        self.name = name
        self.cash_bal = cash_bal
        self.holdings = {}
        if holdings:
            if hasattr(holdings, "symbol"):
                self.holdings[holdings.symbol] = holdings
            #TODO: fix this...assume a list of holdings objects passed in
            else:
                for itm in holdings:
                    self.holdings[itm.symbol] = itm

        return

    def add_holding(self, holding):
        """ Add to container (dict) for holdings (symbol is key)
        """

        self.holdings[holding.symbol] = holding
        print "Added holding %s" % holding
        return

    def remove_holding(self, symbol):
        """ Remove entry from holding dict for given symbol
        """

        del self.holdings[symbol]
        return
    
    def pprint(self):
        
        for holding in self.holdings:
            print "%s Holdings:" % holding
            for position in self.holdings[holding].positions:
                print "%s\t%s\t%s\t%s\t%s\t%s" % (position.trans_date, position.side,
                    position.description, position.qty, position.price, position.total_amt)
                

class Holding():
    """ Queue for held positions in the same security (as identified
        by symbol).  The removal of entries are handled in a 'fifo'
        or a 'lifo' order, depending on the order argument of the
        remove_from method.
    """

    def __init__(self):
        self.qty = 0.0
        self.symbol = ""
        self.positions = []
        return

    def adjust_holding(self, position):
        """ Adjusts a holding based on a provided position argument.
            inputs:
                position - the position causing the alteration
            returns:
                None

            All the branching logic is handled with this method, and add_item or remove_item
            are called depending on the attributes of the position object passed in.
        """

    def add_to(self, position):
        if not self.symbol:
            self.symbol = position.symbol
        if position.symbol==self.symbol:
            self.qty += position.qty
            self.positions.append(position)
        else:
            raise AttributeError
        return
        
    def remove_from(self, position, order="fifo"):
        """ given a position designated as a removal, adjust
            the quantity (qty) and remove or alter the relevant
            position entries in the order designated by 'order'
            
            inputs:
                position - the position causing the alteration
                order - one of 'fifo' or 'lifo'
                
            returns:
                None
            
            'fifo' - first-in-first-out
            'lifo' - last-in-first-out

            This method implements a queue reduction of holdings by the amount specified in the
            provided 'position' quantity (qty).  This method also serves the purpose of populating a 'statement'
            property -- capturing a P/L amount based on the prior costs.

            The queueing actually handles the four cases of a) zeroing out a holding, b) reducing a holding
            c) eliminating a holding and recursing to the next held item, or d) eliminating a holding with no
            next item, and adding a holding in the other direction.
        """
        
        if order=='fifo':
            pos_idx = 0
        elif order=='lifo':
            pos_idx = -1
        
        if not self.positions:
            raise KeyError("No positions in Holding to remove")

            
        self.positions.sort()
        idx_pos = self.positions[pos_idx]
        idx_qty = idx_pos.qty
        
        # Test scenarios for position removal
        #   First scenario: indicated qty is the same as the position entry
        #   qty next in the queue.  If so, simply adjust the qty total and 
        #   remove that entry in the queue.
        if -position.qty == idx_qty:
            # Assume an opposite signed qty.
            self.qty += position.qty
            del self.positions[pos_idx]
            
        # Second scenario: indicated qty is greater than the position entry
        #   qty next in the queue.  If so, adjust the qty total by the amount
        #   of the qty of the position next in the queue, remove that entry
        #   from the queue and recurse the remove_from call with the amount
        #   of the difference between the indicated amount and the queue
        #   entry amount.
        elif -position.qty > idx_qty:

            remaining = position.qty + idx_qty
            self.qty -= idx_qty
            del self.positions[pos_idx]
            
            share_ratio = remaining/position.qty
            position.qty = remaining
            
            # prorate the fees
            position.fee = position.fee - share_ratio*position.fee
            self.remove_from(position)
        
        # Third scenario: indicated qty is less than the position entry
        #   qty next in the queue.  If so, adjust the queued qty and the
        #   holdings qty, as well as prorating the remaining queued fees.
        elif -position.qty < idx_qty:
            remaining = idx_qty + position.qty
            self.qty += position.qty  
            # alter the 'indexed' position to reflect fee and qty changes
            self.positions[pos_idx].qty = remaining
            share_ratio = remaining/idx_qty
            self.positions[pos_idx].fee = self.positions[pos_idx].fee * share_ratio
        return
        
    def __repr__(self):
        """ Custom representation of holding object. """
        symbol = "No Holding"
	if hasattr(self, "positions"):
            if self.positions:
                symbol = self.positions[0].symbol
        
        return "<%s, qty: %s as %s>" % (symbol, self.qty, self.positions)
    
    
    def transact(self, symbol, cost, proceeds, fees):
        """ posts transaction entry based on costs and proceeds """
        
        raise NotImplementedError
        
        
if __name__ == '__main__':
    main()

