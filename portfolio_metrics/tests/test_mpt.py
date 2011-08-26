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

def test_rate_array():
    """ simple test of pricearray in, ratearray out."""
    dt = np.dtype([('date', ('<M8[us]', {})), ('rate', '<f8')])
    pa = np.array([["2001-1-1", 100.0], ["2001-1-2", 101.0],
                   ["2001-1-1", 100.0], ["2001-1-2", 101.0],
                   ["2001-1-1", 100.0], ["2001-1-2", 101.0]])
    ra = metrics.rate_array(pa)
    np.testing.assert_array_equal(pa, ra)
    
if __name__ == '__main__':
    unittest.main()