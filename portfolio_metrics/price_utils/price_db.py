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
import sys
import datetime, time
import csv

# Major library imports
import numpy as np
import sqlite3

# Local imports
import price_data


def adapt_datetime(dt):
    # Get the datetime for the POSIX epoch.
    epoch = datetime.datetime.utcfromtimestamp(0.0)
    elapsedtime = dt - epoch
    # Calculate the number of milliseconds.
    seconds = float(elapsedtime.days)*24.*60.*60. + float(elapsedtime.seconds) + float(elapsedtime.microseconds)/1000000.0
    return seconds


def convert_datetime(tf):
    # Note: strange math is used to account for daylight savings time and 
    #    times in the Eastern (US) time zone (e.g. EDT)
    tf = float(tf)
    edt_adjustment = 6 * 60. * 60.
    if time.localtime(tf).tm_isdst:
        edt_adjustment = 5 * 60. * 60.
    return datetime.datetime.fromtimestamp(tf+edt_adjustment)
    
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)


def create_db(filename="test.db"):
    """ Creates database with schema to hold stock data."""
    
    if os.path.exists(filename):
        raise IOError
    
    conn = sqlite3.connect(filename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.execute('''CREATE TABLE stocks (symbol text, date datetime, open float, high float, low float, close float, volume float, adjclose float)''')
    conn.execute('''CREATE UNIQUE INDEX stock_idx ON stocks (symbol, date)''')
    conn.commit()
    conn.close()
    return


def save_to_db(data, dbfilename="data/stocks.db"):
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
        
        c.executemany(sql, data.tolist())
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    change_count = conn.total_changes
    c.close()
    conn.close()
    return change_count


def load_from_db(symbol, startdate, enddate, dbfilename="data/stocks.db"):
    """ Convenience function to pull data out of our price database. """
    
    # TODO: This is convoluted and, most-likely, quite slow... fix later
    dt = np.dtype('M8')
    startdate = time.mktime(np.array(startdate, dtype=dt).tolist().timetuple())
    enddate = time.mktime(np.array(enddate, dtype=dt).tolist().timetuple())
    
    conn = sqlite3.connect(dbfilename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    sql = "SELECT symbol, date as 'date [datetime]', open, high, low, " \
          "close, volume, adjclose from stocks where symbol='%s' and " \
          "date>=%s and  date<=%s" % (symbol, startdate, enddate)
    qry = conn.execute(sql)
    recs = qry.fetchall()

    table = np.array(recs, dtype=price_data.schema)
    
    return table
    
    
def populate_db(symbols, startdate, enddate, dbfilename):
    """ Wrapper function to rifle through a list of symbols, pull the data,
        and store it in a sqlite database file.
        
        Parameters:
        symbols: list of strings or a string representing a csv file path.
            If a csv filepath is provided, the first column will be used for
            symbols.
        startdate: string, a date string representing the beginning date
            for the requested data.
        enddate: string, a date string representing the ending date for the 
            requested data.
    """
    save_count = 0
    rec_count = 0
    if isinstance(symbols, str):
        # Try loading list from a file
        reader = csv.reader(open(symbols))
        
        symbolset = set()
        badchars = ["/", ":", "^", "%", "\\"]

        # pull symbols from file and put into list
        for line in reader:
    
            symb = line[0]
            for itm in badchars:
                symb = symb.replace(itm, "-")
                symbolset.add(symb.strip())
        symbollist = list(symbolset)
    else:
        symbollist = set(symbols)
    
    tot = float(len(symbollist))
    count=0.0
    print "loading data ..."
    for symbol in list(symbollist):
        data = price_data.get_yahoo_prices(symbol, startdate, enddate)
        num_saved = save_to_db(data, dbfilename)
        count+=1.0
        if num_saved:
            save_count+=1
            rec_count+=num_saved
        # Give some indication of progress at the command line
        print symbol + "",
        sys.stdout.flush()

    print "Saved %s records for %s out of %s symbols" % (rec_count,
                                                         save_count,
                                                         len(symbollist))
    
    
def symbol_exists(symbol, dbfilename="data/stocks.db"):
    """ Check for existence of symbol in specified dbfilename.  Returns a 
        tuple of how many records, and the start and end dates of the data
        available for the symbol.
    """
    
    conn = sqlite3.connect(dbfilename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    sql = "SELECT symbol, date as 'date [datetime]' from stocks where symbol='%s';" % (symbol)
    qry = conn.execute(sql)
    recs = qry.fetchall()
    schema = np.dtype({'names':['symbol', 'date'],
                       'formats':['S8', 'M8']})
    table = np.array(recs, dtype=schema)
    startdate = table['date'][0]
    enddate = table['date'][-1]
    return len(table), startdate, enddate
    

def all_symbols(dbfilename="data/stocks.db"):
    """ Convenience function to return a list of all symbols in the 
        database.
    """
    
    conn = sqlite3.connect(dbfilename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    sql = "SELECT DISTINCT symbol from stocks;"
    qry = conn.execute(sql)
    recs = qry.fetchall()
    reclist = [list(rec)[0] for rec in recs]
    return reclist


        
def main():
    pass


if __name__ == '__main__':
    main()

#### EOF ##################################################################
