#!/usr/bin/env python
# encoding: utf-8
"""
tadpole.py

Created by Travis Vaught on 2012-10-22.
Copyright (c) 2012 Vaught Consulting.

License: BSD
"""

# Major package imports
import numpy as np
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
        df[col].replace(np.nan, 0.0)
    
    dff = df[(boughts) | (solds)]
    print dff['DATE']
    print dff['SYMBOL']
    print dff['DESCRIPTION']
    
    port = Portfolio(name="TD Ameritrade - BMP")
    
    # Loop through each Symbol as a holding
    symbs = dff['SYMBOL'].unique()
    
    for symb in symbs:
        dff_symb = dff[symb]
        hld = Holding
    
        for tran in dff_symb.iterrows():
            tran_data = tran[1]
            if tran_data['DESCRIPTION'].startswith("Bought"):
                side = "BUY"
            elif tran_data['DESCRIPTION'].startswith("Sold"):
                side = "SELL"
            else:
                side = "UNKNOWN"
    
            p = Position(symbol=tran_data['SYMBOL'],
                     id=tran_data['TRANSACTION ID'],
                     description=tran_data['DESCRIPTION'],
                     trans_date=tran_data['DATE'],
                     qty=tran_data['QUANTITY'],
                     price=tran_data['PRICE'],
                     fee=tran_data['COMMISSION'] + tran_data['REG FEE'],
                     total_amt=tran_data['AMOUNT'],
                     side = side)
    
            if side == "BUY":
                print "Adding %s to Portfolio" % p
                port.add_to(p)
        
            elif side == "SELL":
                print "Removing %s from Portfolio" % p
                port.remove_from(p)
        
        
    print port
        #if tran['DESCRIPTION'].startswith("Bought")
        #    port.add_to(Position(transaction['']))
    
    return port
    
if __name__ == '__main__':
    port = main()

