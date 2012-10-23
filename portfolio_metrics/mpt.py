#!/usr/bin/env python
# encoding: utf-8
"""
mpt.py

Created by Travis Vaught on 2011-08-13.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD
"""

# Standard library imports ####
import copy

# Major library imports ####
import numpy as np
from scipy.interpolate import interp1d

# Local imports ####
from metrics import (annualized_adjusted_rate, beta_bb, 
    expected_return, rate_array, volatility)

import price_utils

# Constants ####
price_schema = np.dtype({'names':['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'adjclose'],
                         'formats':['S8', 'M8', float, float, float, float, float, float]})


def align_dates(olddates, olddata, newdates):
    """ Function to align data given two differing date streams.
        Parameters:
            olddates: array of datetime64 type representing dates with misalignment
            olddata: array floats representing data for olddates
            newdates: array of datetime64 type representing new dates with which we should align.
        Returns:
            newdata: array of data aligned with newdates
    """

    olddatefloats = np.array([price_utils.adapt_datetime(dt) for dt in olddates.tolist()])
    newdatefloats = np.array([price_utils.adapt_datetime(dt) for dt in newdates.tolist()])
    datesbelow = newdatefloats < olddatefloats[0]
    datesabove = newdatefloats > olddatefloats[-1]
    dts = ~(datesabove | datesbelow)

    f = interp1d(olddatefloats, olddata)

    newdata = f(newdatefloats[dts])

    return newdata


class Stock(object):
    
    def __init__(self, symbol, startdate="1995-1-1",
        enddate="2011-7-31", dbfilename='data/stocks.db', bench='LALDX', rfr=0.015):
        """ Stock object with some methods to call metrics functions to pre-
            populate some attributes, as well as methods to impute to a given
            datearray.
        """

        self.symbol = symbol
        self.benchsymbol = bench
        self.startdate = startdate
        self.enddate = enddate
        self.rfr = rfr
        self.stock_data_cache = None
        self.bench_data_cache = None
        
        self.bench_data = price_utils.load_from_db(bench,
                                        self.startdate,
                                        self.enddate,
                                        dbfilename=dbfilename)
        self.stock_data = price_utils.load_from_db(symbol,
                                        self.startdate,
                                        self.enddate,
                                        dbfilename=dbfilename)

        # Bail out of initialization if there is no data
        if len(self.stock_data)==0:
            return
        sdates = self.stock_data['date']

        # Not sure about this approach in using return values...seemed useful
        # at the time.
        if not self.impute_to(sdates):
            self.update_metrics()


    def impute_to(self, dts, cache_originals=False):
        """ Method impute stock data to match given dates.

            Note: this only works when _shortening_ the data and filling in
                  a few missing values.
        """
        # Check alignment of bench_data as a test whether we need to impute
        #   TODO: this is a bit hackish
        if not np.alltrue(self.bench_data['date']==dts):
            sdata = []
            ssymb = [self.benchsymbol for x in range(len(dts))]
            bdata = []
            bsymb = [self.benchsymbol for x in range(len(dts))]

            for fld in price_schema.names[2:]:
                sdata.append(align_dates(self.stock_data['date'], self.stock_data[fld], dts))
                bdata.append(align_dates(self.bench_data['date'], self.bench_data[fld], dts))

            srecs = zip(ssymb, dts, *tuple(sdata))
            brecs = zip(bsymb, dts, *tuple(bdata))

            if cache_originals:
                self.stock_data_cache = self.stock_data
                self.bench_data_cache = self.bench_data

            self.stock_data = np.array(srecs, dtype=price_schema)
            self.bench_data = np.array(brecs, dtype=price_schema)
            self.update_metrics()
            return True
        else:
            return False


    def update_metrics(self):
        self.dates = self.stock_data['date']
        self.stock_prices = self.stock_data['adjclose']
        self.bench_prices = self.bench_data['adjclose']
        self.ratearray = rate_array(self.stock_data)
        self.bencharray = rate_array(self.bench_data)

        # TODO: Not sure if these are the metrics I'm looking for...
        self.annual_volatility = volatility(self.ratearray)
        self.beta = beta_bb(self.ratearray, self.bencharray)
        self.annualized_adjusted_return = annualized_adjusted_rate(self.ratearray, rfr=0.01)
        self.expected_return = expected_return(self.ratearray,
                                               self.bencharray,
                                               rfr=self.rfr)
        return


class Portfolio(object):
    """ Portfolio to aggregate stocks and calculate portfolio metrics along 
        the lines of MPT.  This is an implementation of the approach 
        described here:
        http://www.stanford.edu/~wfsharpe/mia/opt/mia_opt1.htm
    """
    
    def __init__(self, symbols=["VISGX", "VGPMX", "VGSIX"],
                       weights = "equal",
                       startdate="2004-1-1",
                       enddate="2011-8-12",
                       dbfilename="data/indexes.db"):

        self.startdate = startdate
        self.enddate = enddate
        self.dbfilename = dbfilename

        self.stocks = {}

        # Get stock data:
        print "Adding: ",
        for symbol in symbols:
            print symbol,
            s = Stock(symbol, startdate, enddate, self.dbfilename)

            # Only add it to the portfolio if it has data
            if len(s.stock_data)>0:
                self.stocks[symbol] = s

        self.symbols = self.stocks.keys()
        self.symbols.sort()
        self.level_lengths()
        
        if weights=="equal":
            self.weights = dict(zip(self.symbols, self.equal_weight()))
        else:
            # This will not add up to 1.0 if any symbols are dropped due to
            #   a lack of data.  TODO: figure out a better approach.
            self.weights = dict(zip(self.symbols, weights))
        
        return
    

    def level_lengths(self):
        """ Method to truncate earlier dates in stock recarrays where they
            all match.  Only do this for ratearray and bencharray objects
            in the stock objects for now.  This also assumes that the bench-
            mark data will always be longer than the shortest stock data.
            TODO: there are still problems with the benchmark data needing 
            truncation/imputing.
        """

        # Start with a very early date.
        latest_start_date = np.datetime64("1800-1-1")
        symbs = self.symbols
        s = self.stocks
        
        # Find shortest stock array length.
        #print "\nLeveling: ",
        for symb in symbs:
            print symb,
            if latest_start_date < s[symb].stock_data['date'][0]:
                latest_start_date = s[symb].stock_data['date'][0]
                latest_start_symb = symb
                
        # Assume symbol with latest start is best choice to impute
        # other stock data toward.
        for symb in symbs:
            s[symb].impute_to(s[latest_start_symb].stock_data['date'], cache_originals=True)

        return
        
        
    def equal_weight(self):
        return [1.0/len(self.symbols) for symbol in self.symbols]
        
        
    def evaluate_holdings(self):
        """ This method updates the return for the portfolio
            overall, based on the weights and returns of the components
            in the portfolio.  It returns a tuple of (variance,
            portfolio_expected_return)
        """
        
        port_return = 0.0
        
        for symbol in self.symbols:
            port_return += (self.stocks[symbol].annualized_adjusted_return * self.weights[symbol])
            
        self.portfolio_return = port_return
            
        variance = self.calc_variance()
        return variance, port_return

    def calc_port_rates(self):

        port_ratearray = None

        for symbol in self.symbols:
            srate = self.stocks[symbol].ratearray
            weight = self.weights[symbol]
            # Construct an empty portfolio rate array if there is not one.
            if port_ratearray is None:
                dts = srate['date']
                port_ratearray =  np.array(zip(dts, np.zeros(srate.shape)),
                    dtype=srate.dtype)
            port_ratearray['rate'] += srate['rate'] * weight

        self.port_ratearray = port_ratearray
        return port_ratearray

    
    def calc_variance(self):
        """ A method for returning the portfolio variance.
        """
        
        port_ratearray = self.calc_port_rates()
        
        self.volatility = volatility(port_ratearray)
        self.variance = self.volatility**2
        
        return self.variance
        
        
    def calc_marginal_utility(self, rt=0.20):
        """ Use Sharpe's method for mu calculation, given by:
            
            mu = e - (1/rt)*2*C*x
            
            where:
            e = vector of expected returns of stocks in portfolio
                TODO: Note: Sharpe's "expected returns" are similar to the 
                      mean of the historical returns -- not the CAPM
                      definition of "expected return."  Therefore, we use the 
                      annualized_adjusted_return for now.
            rt = investor risk tolerance
            C = Covariance matrix of existing portfolio holdings
            x = The current portfolio allocation
            
        """
        
        e_ary = np.array([self.stocks[symbol].annualized_adjusted_return for symbol in self.symbols])
        
        e = np.mat(e_ary).T
        
        ratelist = []
        
        for symb in self.symbols:
            ratelist.append(self.stocks[symb].ratearray['rate'].tolist())

        rates = np.array(ratelist, dtype=float)
        
        cv = np.cov(rates)
        C = np.mat(cv)
        
        weights = np.array([self.weights[symbol] for symbol in self.symbols])
        x = np.mat(weights).T
        
        mu = e - (1/rt)*2*C*x
    
        return mu
    
    def step_port_return(self, rt=0.20,
                         lower_bound_weight=-2.0,
                         upper_bound_weight=2.0):
        """ A method for returning a portfolio with the weights for the
            optimal rate of return given a maximum variance allowed.
            
            This also uses Sharpe's procedures for calculating the optimal
            buy/sell ratio for a two-stock swap.
            
            TODO: Note: This method currently allows leverage -- no limits on shorting
                or lower and upper bounds of ownership.
        """
        
        mubuy = -1E200
        musell = 1E200
        
        p1 = self
        if getattr(p1, "port_opt", None) is None:
            self.port_opt = p2 = copy.deepcopy(p1)
        else:
            p2 = self.port_opt
        
        weights = np.array([p2.weights[symbol] for symbol in p2.symbols])
        x = np.mat(weights).T
        
        mu = p2.calc_marginal_utility(rt)
        
        for i in range(len(p2.symbols)):
            if x[i] < upper_bound_weight: # possible buy
                if mu[i,0] > mubuy:
                    mubuy = mu[i,0]
                    ibuy = i
            
            if x[i] > lower_bound_weight:  # possible sell
                if mu[i,0] < musell:
                    musell = mu[i,0]
                    isell = i
        
        if (mubuy-musell)<=0.0001:
            ibuy=isell=0
        
        s = np.zeros(mu.shape)
        s[isell]=-1.0
        s[ibuy]=1.0
        s = np.mat(s)
        
        rates = np.array([p2.stocks[symbol].ratearray['rate'] for symbol in p2.symbols])
        C = np.mat(np.cov(rates))
        
        k0 = s.T*mu
        k1 = (s.T*C*s)/rt
        
        amat = k0/(2*k1)
        a = amat[0,0]
        
        # a change of weights according to 'a' will yield a utility
        # change as indicated below.  This is not currently returned or used anywhere,
        # but it's calculated here for potential future use.
        cu = k0*a - k1*(a**2)
        
        symb_sell = p2.symbols[isell]
        symb_buy = p2.symbols[ibuy]
        if symb_sell == symb_buy:
            a = 0.0
        
        # Keep within the bounds
        if p2.weights[symb_sell]-a < lower_bound_weight:
            a = p2.weights[symb_sell]-lower_bound_weight
        if p2.weights[symb_buy]+a >upper_bound_weight:
            a = upper_bound_weight-p2.weights[symb_buy]
            
        p2.weights[symb_sell] = p2.weights[symb_sell]-a
        p2.weights[symb_buy] = p2.weights[symb_buy]+a
        
        #print("Recommend Sell: %s" % symb_sell)
        #print("Recommend Buy: %s" % symb_buy)
        #print("Affect on Portfolio Return: %s" % cu)
            
        return a
        
    def optimize_portfolio(self, rt=0.10,
                           lower_bound_weight=-0.50,
                           upper_bound_weight=1.5):
        """ Simple optimization wrapper to set bounds and limit iterations """

        a = 1.0
        count = 0
        
        while a>0.00001:
            a = self.step_port_return(rt, lower_bound_weight,
                                      upper_bound_weight)

            count+=1
        
        result = self.port_opt.evaluate_holdings()
        variance = round(result[0],3)
        ret = round(result[1]*100.,3)
        
        print("Optimization completed in [ %s ] iterations." % count)
        print("Ending weights:\n%s" % self.port_opt.weights)
        print("Volatility: %s and Portfolio Return: %s%%" % (np.sqrt(variance), ret))
        opt_rate_array = self.port_opt.calc_port_rates()
        print("Portfolio Rate Array:%s\n" % opt_rate_array[:10])
        
        
# EOF ####################################################################


