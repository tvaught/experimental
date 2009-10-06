#!/usr/bin/env python
# encoding: utf-8
"""
portfolio.py

Created by Travis Vaught on 2009-10-03.
Copyright (c) 2009 Vaught Consulting. All rights reserved.

License: BSD

"""

# Enthought imports
from enthought.traits.api import (HasTraits, Float, Instance, List)

# Local imports
from position import Position

class Holding(HasTraits):
    """ Queue for held positions in the same security (as identified
        by symbol).  The removal of entries are handled in a 'fifo'
        or a 'lifo' order, depending on the order argument of the
        remove_from method.
    """

    # Total quantity for a particular holding
    qty = Float
    
    # List of positions making up the holding
    positions = List(Instance(Position))
    
    def add_to(self, position):
        self.qty += position.qty
        self.positions.append(position)
        
    def remove_from(self, position, order="fifo"):
        """ given a position designated as a removal, adjust
            the quantity (qty) and remove or alter the relevant
            position entries in the order designated by 'order'
            
            inputs:
                position - the position causing the alteration
                order - one of 'fifo', 'lifo' or 'wifo'
                
            returns:
                None
            
            'fifo' - first-in-first-out
            'lifo' - last-in-first-out
            'wifo' - worst-in-first-out - not implemented (need to figure out
                how to do sorting of positions flexibly)
        """
        
        if order=='fifo':
            pos_idx = 0
        elif order=='lifo':
            pos_idx = -1
        elif order=='wifo':
            raise NotImplementedError
        
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
        
        if self.positions:
            symbol = self.positions[0].symbol
        return "<%s, qty: %s as %s>" % (symbol, self.qty, self.positions)
    
    
    def transact(self, symbol, cost, proceeds, fees):
        """ posts transaction entry based on costs and proceeds """
        
        raise NotImplementedError
        
        
if __name__ == '__main__':
    main()

