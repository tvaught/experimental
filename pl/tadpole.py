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
import position
import portfolio

def main():
    df = pd.read_csv(open('./test/transtest.csv'), comment="***")
    
    bought_filter = lambda x: str(x).startswith("Bought")
    sold_filter = lambda x: str(x).startswith("Sold")
    
    boughts = df['DESCRIPTION'].map(bought_filter)
    solds = df['DESCRIPTION'].map(sold_filter)
    
    # Allow the fees to be summed by replacing nans with 0.0s
    fee_cols = ["COMMISSION", "REG FEE"]
    for col in fee_cols:
        df[col].replace(np.nan, 0.0)
    
    dff = df[(boughts) | (solds)]
    
    port = portfolio.Portfolio(name="TD Ameritrade - BMP")
    
    # Loop through each Symbol as a holding
    symbs = np.asarray(dff['SYMBOL'].unique(), dtype='S50')
    
    for symb in symbs:
        # Filter for current symbol
        dff_symb = dff[dff['SYMBOL']==symb]
        hld = portfolio.Holding()
        
        # Populate a holding with all positions
        for tran in dff_symb.iterrows():
            tran_data = tran[1]
            if tran_data['DESCRIPTION'].startswith("Bought"):
                side = "BUY"
            elif tran_data['DESCRIPTION'].startswith("Sold"):
                side = "SELL"
            else:
                side = "UNKNOWN"
    
            p = position.Position(symbol=tran_data['SYMBOL'],
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
                hld.add_to(p)
        
            elif side == "SELL" and hasattr(hld, "positions"):
                print "Removing %s from Portfolio" % p
                hld.remove_from(p)
            
            else:
                print "Adding short position %s to Portfolio" % p
                hld.add_to(p)
        
        port.add_holding(hld)
        
    port.pprint()
        #if tran['DESCRIPTION'].startswith("Bought")
        #    port.add_to(Position(transaction['']))
    
    return port
    
if __name__ == '__main__':
    port = main()

