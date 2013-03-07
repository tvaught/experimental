#!python

# Author: Travis N. Vaught
# Copyright (c)2013, Vaught Management, LLC
# License: BSD

# Major package imports
import pandas
import numpy as np

# Local library imports
import transaction


# Load from test file
f = open('transactions2012.csv', 'ra')

trns = pandas.read_csv(f)

tlist = []

for i in range(len(trns.DATE)):
    t = transaction.Transaction(
