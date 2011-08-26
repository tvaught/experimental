#!/usr/bin/env python
# encoding: utf-8
"""
metrics.py

Created by Travis Vaught on 2011-08-25.
Copyright (c) 2011 Vaught Consulting. All rights reserved.
"""

def alpha(rates, bench_rates):
    """ The intercept of the market returns vs. the benchmark returns 
        
        Parameters:
         - market_rate_array: 1d array of return rates for market in question
         - benchmark_rate_array: 1d array of return rates for benchmark to
           compare against
    """
    
    return polyfit(bench_rates, rates,1)[1]


def annualized_rate(dates, rates):
    """ Calculate the annualized return rate given periodic rates """
    
    duration = dates[-1]-dates[0]
    yrs = float(duration.days)/float(CALENDAR_DAYS_PER_YEAR)
    total_return = chain_linked_return(rates)

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
    yrs = float(duration.days)/float(CALENDAR_DAYS_PER_YEAR)
    periods_per_year = len(dates)/yrs
    
    if not hasattr(rfr, '__iter__'):
        # calculate simple rate array for risk_free_rate
        # TODO: make sure we're explicit about the proper (simple vs. compounded) way
        #       to specify the risk_free_rate when it is provided as an array
        rfr = rfr*(np.ones(len(rates)))/periods_per_year
    else:
        rfr = np.array(rfr)
        
    # get adjusted rate array (simple rates)
    adj_ra = sum((rates - rfr))/yrs

    return adj_ra


def beta(rates, bench_rates):
    """ The slope of the market returns vs. the benchmark returns
        
        Parameters:
         - rates: 1d array of return rates for market in question
         - bench_rates: 1d array of return rates for benchmark to
           compare against
    """
    
    return polyfit(bench_rates, rates, 1)[0]

def beta_bb(rates, bench_rates):
    """ The slope of the market returns vs. the benchmark returns
        * adjusted using Bloomberg adjustment factor
        
        Parameters:
         - rates: 1d array of return rates
         - bench_rates: 1d array of return rates for benchmark to
           compare against
        Returns:
         - float
    """
    
    return (0.33 + 0.67 * beta(rates, bench_rates))
    

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
    
    
def expected_return(dates, rates, bench_rates, rfr=0.0):
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
    
    betai = beta_bb(rates, bench_rates)
    erm = annualized_adjusted_rate(dates, bench_rates, rfr)
    eri = rfr + betai*(erm-rfr)
    
    return eri


def rate_array(pricearray, startprice=None, priceused='adjclose'):
    """ Converts a record array of prices into an array of simple return rates
    
        Parameters:
        -----------
         - pricearray: array
           1d array of price data (i.e. daily adj. close data)
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
    
    for price in prices:
        rates.append([price['date'], (price[priceused]/opn)-1 ])
        opn = price[priceused]
        
    return array(rates)
    
    
# EOF ####################################################################


