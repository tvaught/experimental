#!/usr/bin/env python
# encoding: utf-8
"""
date_util_test.py

Created by Travis Vaught on 2009-09-29.
Copyright (c) 2009 Vaught Consulting. All rights reserved.

License: BSD

"""

# Local package imports
from date_util import dt_from_timestamp, dt_to_timestamp


def date_util_test():
    """ Simple test of correctly transforming a timestamp to a python datetime,
        and back to a timestamp
    """
    
    # test a not-very-random sequence of times
    for ts in range(0, 1250000000, 321321):
        # simply see if we can round-trip the timestamp and get the same result
        dt = dt_from_timestamp(ts)
        ts2 = int(dt_to_timestamp(dt))
        assert ts2 == ts


if __name__ == '__main__':
    date_util_test()

#### EOF ####################################################################