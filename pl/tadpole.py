#!/usr/bin/env python
# encoding: utf-8
"""
tadpole.py

Created by Travis Vaught on 2012-10-22.
Copyright (c) 2012 Vaught Consulting.

License: BSD
"""

import pandas as pd

def main():
    df = pd.read_csv(open('./test/transtest.csv'), comment="***")
    
    bought_filter = lambda x: str(x).startswith("Bought")
    sold_filter = lambda x: str(x).startswith("Sold")
    
    boughts = df['DESCRIPTION'].map(bought_filter)
    solds = df['DESCRIPTION'].map(sold_filter)

    dff = df[(boughts) | (solds)]
    print dff['DATE']
    print dff['SYMBOL']
    print dff['DESCRIPTION']
    

    
if __name__ == '__main__':
    main()

