#!/usr/bin/env python
# encoding: utf-8
"""
db_tools.py

Created by Travis Vaught on 2011-08-24.
Copyright (c) 2011 Vaught Consulting.
License: BSD
"""

# Standard library imports
import os
import datetime, time

# Major library imports
import numpy as np
import sqlite3

# Local imports
import price_data

def adapt_datetime(dt):
    return (dt - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)

def convert_datetime(tf):
    return datetime.fromtimestamp(tf)
    
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

def create_db(filename="test.db"):
    if os.path.exists(filename):
        raise IOError
    
    conn = sqlite3.connect(filename)
    conn.execute('''CREATE TABLE stocks (symbol text, date datetime, open float, high float, low float, close float, volume float, adjclose float)''')
    conn.execute('''CREATE UNIQUE INDEX stock_idx ON stocks (symbol, date)''')
    conn.commit()
    conn.close()
    

def save_to_db(data, dbfilename="stocks.db"):
    """ Utility function to save financial instrument price data to an SQLite
        database file."""


    if not os.path.exists(dbfilename):
        create_db(dbfilename)

    conn = sqlite3.connect(dbfilename)
    c = conn.cursor()

    # Wrap in a try block in case there's a duplicate given our UNIQUE INDEX
    #     criteria above.
    try:
        sql = "INSERT INTO stocks (symbol, date, open, high, low, close, volume, adjclose) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        #print sql
        c.executemany(sql, data.tolist())
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    c.close()
    conn.close()

def load_from_db(symbol, startdate, enddate, dbfilename):
    """ Convenience function to pull data out of our price database. """
    
    # TODO: This is convoluted and, most-likely, quite slow... fix later
    dt = np.dtype('M8')
    startdate = time.mktime(np.array(startdate, dtype=dt).tolist().timetuple())
    enddate = time.mktime(np.array(enddate, dtype=dt).tolist().timetuple())
    
    print startdate, enddate
    
    conn = sqlite3.connect(dbfilename)
    sql = "SELECT symbol, date as 'date [datetime]', open, high, low, " \
          "close, volume, adjclose from stocks where symbol='%s' and " \
          "date>=%s and  date<=%s" % (symbol, startdate, enddate)
    print sql
    qry = conn.execute(sql)
    recs = qry.fetchall()
    print recs
    table = np.array(recs, dtype=price_data.schema)
    
    return table
    
    
def main():
    pass


if __name__ == '__main__':
    main()

#### EOF ##################################################################
