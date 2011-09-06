#!/usr/bin/env python
# encoding: utf-8
"""
metrics.py

Created by Travis Vaught on 2011-08-25.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD
"""

# Major library imports
import numpy as np
from scipy import arange, array, corrcoef, cov, mean, polyfit, prod, sqrt, \
    sum, var
    
# Constants
HOURS_PER_DAY = 24.0
MINUTES_PER_DAY = 60.0 * HOURS_PER_DAY
SECONDS_PER_DAY = 60.0 * MINUTES_PER_DAY
MICROSECONDS_PER_DAY = 1000000.0 * SECONDS_PER_DAY
CALENDAR_DAYS_PER_YEAR = 365.0
TRADING_DAYS_PER_YEAR = 252.0
WEEKS_PER_YEAR = 52.0
MONTHS_PER_YEAR = 12.0

def alpha(ratearray, bench_ratearray):
    """ The intercept of the market returns vs. the benchmark returns 
        
        Parameters:
         - market_rate_array: 1d array of return rates for market in question
         - benchmark_rate_array: 1d array of return rates for benchmark to
           compare against
    """
    
    return polyfit(bench_ratearray['rate'], ratearray['rate'],1)[1]


def annualized_rate(ratearray):
    """ Calculate the annualized return rate given periodic rates """
    
    duration = ratearray['date'][-1]-ratearray['date'][0]
    yrs = float(duration.tolist().days)/float(CALENDAR_DAYS_PER_YEAR)
    total_return = chain_linked_return(ratearray)

    # TODO: This needs to be checked
    return (total_return+1)**(1/yrs)-1
    

def annualized_adjusted_rate(ratearray, rfr=0.0):
    """ Returns the annualized adjusted rate of return
        
        Parameters:
         - ratearray: array
           record array of dates and rates  dtype([('date', ('<M8[us]', {})), ('rate', '<f8')])
         - rfr: float or 1d array of floats
           Provided as the simple periodic rate
    """
    
    dates = ratearray['date']
    startdate = dates[0]
    enddate = dates[-1]
    
    duration = enddate-startdate
    yrs = float(duration.tolist().days)/float(CALENDAR_DAYS_PER_YEAR)
    periods_per_year = len(dates)/yrs
    
    if not hasattr(rfr, '__iter__'):
        # calculate simple rate array for risk_free_rate
        # TODO: make sure we're explicit about the proper (simple vs. compounded) way
        #       to specify the risk_free_rate when it is provided as an array
        rfr = rfr*(np.ones(len(ratearray)))/periods_per_year
    else:
        rfr = np.array(rfr)
        
    # get adjusted rate array (simple rates)
    adj_ra = sum((ratearray['rate'] - rfr))/yrs

    return adj_ra


def beta(ratearray, bench_ratearray):
    """ The slope of the market returns vs. the benchmark returns
        
        Parameters:
         - ratearray: recarray of dates and return rates
         - bench_ratearray: recarray of return rates for benchmark instrument
    """
    
    return polyfit(bench_ratearray['rate'], ratearray['rate'], 1)[0]

def beta_bb(ratearray, bench_ratearray):
    """ The slope of the market returns vs. the benchmark returns
        * adjusted using Bloomberg adjustment factor
        
        Parameters:
         - ratearray: recarray of dates and return rates
         - bench_rates: recarray of dates and return rates for benchmark
        Returns:
         - float
    """
    
    return (0.33 + 0.67 * beta(ratearray, bench_ratearray))
    

def chain_linked_return(ratearray):
    """ Total return over a period calculated from an
        array of uniform (daily, weekly, monthly) rates of return.
        The period of the rate of return is the period
        included in the rates array.
        
        NOTE: this has the basic effect of compounding over time,
              so the returned rate is as close to "continuous compounding"
              as the periodic compounding calculation would be.
        
        Parameters:
         - rates: 1d float array
           uniform rates of return
    """
        
    return prod(1.0 + ratearray['rate']) - 1.0
    
    
def expected_return(ratearray, bench_ratearray, rfr=0.0):
    """ Calculate the expected return using the Capital Asset
        Pricing Model (CAPM) approach.
        
        Given as:
            E(Ri) = Rf + Betai (E(Rm) - Rf)
        
        Where:
            E(Ri) is the expected return
            Rf is the risk-free rate
            Betai, or the beta, is the sensitivity of the expected excess
                asset returns to the expected market returns.
            E(Rm) is the expected return of the market, which, rather than
                using the geometric mean as advised, we do the brute force
                calculation of the annualized_adjusted_rate for the benchmark.
    """
    
    betai = beta_bb(ratearray, bench_ratearray)
    erm = annualized_adjusted_rate(bench_ratearray, rfr)
    eri = rfr + betai*(erm-rfr)
    
    return eri


def rate_array(pricearray, startprice=None, priceused='adjclose'):
    """ Converts a record array of prices into an array of simple return rates
    
        Parameters:
        -----------
         - pricearray: array
           recarray of price data (i.e. daily adj. close data)
         - startprice: float
           open price, if not provided first day close will be used
         - priceused: string
           one of {'open', 'high', 'low', 'close', 'adjclose'}
           
    """   
    if startprice:
        opn = startprice
    else:
        opn = pricearray[priceused][0]
        
    rates = []
    
    for price in pricearray:
        rates.append((price['date'], (price[priceused]/opn)-1 ))
        opn = price[priceused]
        
    dt_rates = np.dtype({'names':['date', 'rate'],
                        'formats':['M8', float]})
    
    return np.array(rates, dtype=dt_rates)


def sharpe_ratio(ratearray, rfr=0.0):
    """ Sharpe Ratio
        defined as:

        rate_of_return-risk_free_rate/sigma where,
         - rate_of_return: Avg. return (expected return)
         - risk_free_rate: Risk-free rate of Return
         - sigma: standard deviation

        Parameters:
         - ratearray: recarray of dates and rates
         - rfr: float or array of floats the annualized risk_free_rate of return
    """

    excess_return = annualized_adjusted_rate(ratearray, rfr)
    sigma = ratearray['rate'].std()
    return excess_return/sigma
    
def volatility(ratearray, period="d"):
    """ Calculates annualized volatility from an
        array of periodic rates of return.
        
        Parameters:
         - ratearray: recarray of "date" and "rate" data
           uniform rates of return (daily, monthly, etc.)
         - period: string
           "m", "w" or "d"
           TODO: It may be optimal to infer the period from the dates --
               punting on that for now.
    """
    
    if period=="d":
        periods = TRADING_DAYS_PER_YEAR
    elif period=="w":
        periods = WEEKS_PER_YEAR
    elif period=="m":
        periods = MONTHS_PER_YEAR
        
    return sqrt(periods) * ratearray['rate'].std()
    
    
# EOF ####################################################################


