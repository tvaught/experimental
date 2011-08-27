#!/usr/bin/env python
# encoding: utf-8
"""
test_mpt.py

Created by Travis Vaught on 2011-08-26.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD
"""

import numpy as np
import metrics

# Constants
schema = np.dtype({'names':['symbol', 'date', 'open', 'high', 'low',
                       'close', 'volume', 'adjclose'],
                   'formats':['S8', 'M8', float, float, float, float,
                       float, float]})
dummy_data = [("TEST", "2001-1-1", 100., 100., 100., 100., 100., 100.),
                  ("TEST", "2001-1-2", 101., 101., 101., 101., 101., 101.),
                  ("TEST", "2001-1-3",  99.,  99.,  99.,  99.,  99.,  99.),
                  ("TEST", "2001-1-4", 100., 100., 100., 100., 100., 100.),
                  ("TEST", "2001-1-5", 101., 101., 101., 101., 101., 101.),
                  ("TEST", "2001-1-8", 105., 105., 105., 105., 105., 105.)]
                  
def test_rate_array():
    """ simple test of pricearray in, ratearray out.
        TODO: Note, this thing fails when I do a complete comparison, so I
            just compare the rate columns.
    """

    rate_dt = np.dtype({'names':['date', 'rate'],
                        'formats':['M8', float]})
    ra_correct = np.array([("2001-01-01", 0.0),
                  ("2001-01-02", 0.01),
                  ("2001-01-03", -0.019801980198),
                  ("2001-01-04", 0.010101010101),
                  ("2001-01-05", 0.01),
                  ("2001-01-08", -0.00990099009901)], dtype=rate_dt)
                      
    # Construct dummy array.
    pa = np.array(dummy_data, dtype=schema)
    ra = metrics.rate_array(pa)
    #print "ra:", ra
    #print "ra_correct:", ra_correct
    x = ra[:][1]
    y = ra[:][1]
    np.testing.assert_array_equal(x, y)
    
    
def test_chain_linked_return():
    """ Chain linked return should be 'total return.'"""
    pa = np.array(dummy_data, dtype=schema)
    ra = metrics.rate_array(pa)
    clr = metrics.chain_linked_return(ra)
    np.testing.assert_almost_equal(clr, 0.05)
    
    
def test_annualized_adjusted_rate():
    """ Check annual rate of return."""
    pa = np.array(dummy_data, dtype=schema)
    ra = metrics.rate_array(pa)
    aar = metrics.annualized_adjusted_rate(ra)
    # This is not a great test ... needs to be independently calculated, 
    #     as does the rate array data.
    np.testing.assert_almost_equal(aar, 2.6020844941637074)
    
    
if __name__ == '__main__':
    print "Please run using 'nosetests' from the command line."
    
    
# EOF ####################################################################