#!/usr/bin/env python
# encoding: utf-8
"""
tadpole.py

Created by Travis Vaught on 2012-10-22.
Copyright (c) 2012 Vaught Consulting.

License: BSD
"""

# Major package imports
import numpy np
import pandas as pd

# Local imports
from position import Position
from portfolio import Holding

def main():
    df = pd.read_csv(open('./test/transtest.csv'), comment="***")
    
    bought_filter = lambda x: str(x).startswith("Bought")
    sold_filter = lambda x: str(x).startswith("Sold")
    
    boughts = df['DESCRIPTION'].map(bought_filter)
    solds = df['DESCRIPTION'].map(sold_filter)
    
    # Allow the fees to be added by replacing nans with 0.0s
    fee_cols = ["COMMISSION", "REG FEE"]
    for col in fee_cols:
        df[col].replace(nan, 0.0)
    
    dff = df[(boughts) | (solds)]
    print dff['DATE']
    print dff['SYMBOL']
    print dff['DESCRIPTION']
    
    port = Holding(name="TD Ameritrade - BMP")
    
    for tran in dff:
        
        Position(symbol=tran['SYMBOL'],
                 id=tran['TRANSACTION ID'],
                 description=tran['DESCRIPTION'],
                 trans_date=tran['DATE'],
                 qty=tran['QUANTITY'],
                 price=tran['PRICE'],
                 fee=tran['COMMISSION'] + tran['REG FEE']
                 tot_amt=tran['']
                 
                 )
        
        #if tran['DESCRIPTION'].startswith("Bought")
        #    port.add_to(Position(transaction['']))
    
    
if __name__ == '__main__':
    main()

