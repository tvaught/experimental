#!/usr/bin/env python
# encoding: utf-8
"""
price_data.py

Created by Travis Vaught on 2011-08-24.
Copyright (c) 2011 Vaught Consulting. All rights reserved.
"""

from time import localtime, time

def get_yahoo_prices(symbol, start_date, end_date, period='d'):
    """ Fetch prices from Yahoo's finance site. 
        
        Parameters
        ----------
        symbol : str
            The symbol for which to pull data.
        start_date : string, optional
            A string representing a date of the format
            from the number of weeks and end_date.
        end_date : datetime.date, optional
            If provided, the final date in the data. Otherwise, the current date.
        period : 'd', 'w', or 'm'
            A code specifying daily, weekly or monthly prices, respectively.

        Returns
        -------
        table : numpy record array
            This table follows the schema given by web_data.price_schema .
    
    """
    
    
    if start_date is None:
        start_date = local_time(time() - 86400) # Default to yesterday
    else:
        
    time() - 24 * 60 * 60 
    strt = localtime( begin )
    ed = localtime( begin - (self.weeks * 7 * 24 * 60 * 60) )

    url = ('http://table.finance.yahoo.com/table.csv?a=%d&b=%d&c=%d&'
           'd=%d&e=%d&f=%d&s=%s&y=0&g=d&ignore=.csv') % ( 
           (before[1] - 1),    before[2],     before[0],
           (yesterday[1] - 1), yesterday[2],  yesterday[0], symbol)

    fh = urlopen( url )
    date, high, low, open, close, volume = [], [], [], [], [], []
    for line in map( lambda x: x[:-1], fh.readlines()[1:] ):
        items = line.split( ',' )
        
        date.append(   mktime(strptime(items[0], "%d-%b-%y")) )
        open.append(   float( items[1] ) )
        high.append(   float( items[2] ) )
        low.append(    float( items[3] ) )
        close.append(  float( items[4] ) )
        volume.append( float( items[5] ) )
    fh.close()

    price_data = numpy.rec.fromarrays([numpy.array(date), 
                                 numpy.array(high), numpy.array(low), 
                                 numpy.array(open), numpy.array(close)], 
                                names='date,high,low,open,close')
    
    return price_data

def timefloat_from_string(timestring, format="%Y-%m-%d"):
    """ Convert string representation of a date to a timefloat (similar 
        to floats returned by mktime) string or an array of date/time strings
        
        Parameters:
        timestring: string or array of strings, of the given format
        format: string, using standard Python string formats
        
        Returns:
        float or numpy array of floats, depending on input, representing 
        timefloats in the form of seconds since the Epoch.
        """
        
    if isinstance(timestring, np.ndarray):
        dts = []
        for dt in timestring:
            t = time.strptime(dt, format_string)
            dts.append(time.mktime(datetime.date(*t[:3]).timetuple()))
        return np.array(dts)

    else:
        t = time.strptime(timestring, format_string)
        return time.mktime(datetime.date(*t[:3]).timetuple())
        
def timefloat_to_string(timefloat, format="%Y-%m-%d"):
    """ Convert a timefloat (float representing seconds since the Epoch)
        to a string of the designated format
    
        Parameters:
        timefloat: float or numpy array of floats, seconds since the Epoch
        format: string, using standard Python string formatting
        
    """
    
    

def main():
	pass


if __name__ == '__main__':
	main()

