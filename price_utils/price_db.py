#!/usr/bin/env python
# encoding: utf-8
"""
price_db.py

Created by Travis Vaught on 2011-08-24.
Copyright (c) 2011 Vaught Management, LLC.
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
    # Get the datetime for the POSIX epoch.
    epoch = datetime.datetime.utcfromtimestamp(0.0)
    # UTC adjustment for NY markets timezone (needed?)
    dtutc = dt #+ datetime.timedelta(hours=5)
    elapsedtime = dtutc - epoch
    # Calculate the number of milliseconds.
    seconds = float(elapsedtime.days)*24.*60.*60. + float(elapsedtime.seconds) + float(elapsedtime.microseconds)/1000000.0
    return seconds

def convert_datetime(tf):
    # TODO: This part smells bad ... is there a better (faster) way to return
    #     something that accounts for Daylight Savings Adjustments in NY?
    tf = float(tf)
    dst_adjustment = 6 * 60. * 60.
    if time.localtime(tf).tm_isdst:
        dst_adjustment = 5 * 60. * 60.
    return datetime.datetime.fromtimestamp(tf+dst_adjustment)
    
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

def create_db(filename="test.db"):
    if os.path.exists(filename):
        raise IOError
    
    conn = sqlite3.connect(filename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.execute('''CREATE TABLE stocks (symbol text, date datetime, open float, high float, low float, close float, volume float, adjclose float)''')
    conn.execute('''CREATE UNIQUE INDEX stock_idx ON stocks (symbol, date)''')
    conn.commit()
    conn.close()
    

def save_to_db(data, dbfilename="stocks.db"):
    """ Utility function to save financial instrument price data to an SQLite
        database file."""


    if not os.path.exists(dbfilename):
        create_db(dbfilename)

    conn = sqlite3.connect(dbfilename,
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
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
    
    conn = sqlite3.connect(dbfilename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    sql = "SELECT symbol, date as 'date [datetime]', open, high, low, " \
          "close, volume, adjclose from stocks where symbol='%s' and " \
          "date>=%s and  date<=%s" % (symbol, startdate, enddate)
    print sql
    qry = conn.execute(sql)
    recs = qry.fetchall()
    print recs
    table = np.array(recs, dtype=price_data.schema)
    
    return table, recs
    
    
def main():
    pass


if __name__ == '__main__':
    main()

#### EOF ##################################################################
