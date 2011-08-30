#!/usr/bin/env python
# encoding: utf-8
"""
mpt.py

Created by Travis Vaught on 2011-08-13.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD
"""

# Standard library imports ####
import datetime
import copy

# Major library imports ####
import numpy as np
from scipy.interpolate import interp1d
import sqlite3

# Local imports ####
from metrics import (annualized_adjusted_rate, beta_bb, 
    expected_return, rate_array, volatility, TRADING_DAYS_PER_YEAR)
    
import price_utils

# Constants ####
price_schema = np.dtype({'names':['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'adj_close'], 'formats':['S8', long, float, float, float, float, float, float]})


class Stock(object):
    
    def __init__(self, symbol, startdate="1995-1-1",
        enddate="2003-7-31", dbfilename='data/indexes.db', bench='^GSPC', rfr=0.015):
        self.symbol = symbol
        self.startdate = startdate
        self.enddate = enddate
        self.rfr = rfr
        
        self.bench_data = price_utils.load_from_db(bench, 
                                        self.startdate,
                                        self.enddate,
                                        dbfilename=dbfilename)
        self.stock_data = price_utils.load_from_db(symbol,
                                        self.startdate,
                                        self.enddate,
                                        dbfilename=dbfilename)

        
        if len(self.bench_data)!=len(self.stock_data):
            print("Full matching stock data not available: needs truncation")
        self.update_metrics()
        
        
    def update_metrics(self):
        self.ratearray = rate_array(self.stock_data)
        self.bencharray = rate_array(self.bench_data)
        # TODO: Not sure if these are the metrics I'm looking for...
        self.annual_volatility = volatility(self.ratearray)
        #self.beta = beta_bb(self.ratearray, self.bencharray)
        self.annualized_adjusted_return = annualized_adjusted_rate(self.ratearray, rfr=0.01)
        #self.expected_return = expected_return(self.ratearray,
        #                                       self.bencharray,
        #                                       rfr=self.rfr)
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
        
        symbols.sort() #TODO: is this advisable?
        self.symbols = symbols
        
        if weights=="equal":
            self.weights = dict(zip(symbols, self.equal_weight()))
        else:
            self.weights = dict(zip(symbols,weights))
        
        self.startdate = startdate
        self.enddate = enddate
        self.dbfilename = dbfilename
        
        self.get_initial_stock_data()
        self.level_lengths()
        
        return

    def get_initial_stock_data(self):
        self.stocks = {}
        for symbol in self.symbols:
            self.add_stock(symbol, self.weights[symbol],
                           self.startdate, self.enddate)
        return
    
    def add_stock(self, symbol, weight, startdate, enddate):
        print "Adding:", symbol
        self.stocks[symbol] = Stock(symbol, startdate, enddate,
                                    self.dbfilename)
        self.weights[symbol] = weight
    

    def level_lengths(self):
        """ Method to truncate earlier dates in stock recarrays where they
            all match.  Only do this for ratearray and bencharray objects
            in the stock objects for now.  This also assumes that the bench-
            mark data will always be longer than the shortest stock data.
        """
        
        dt_rates = np.dtype({'names':['date', 'rate'],
                        'formats':['M8', float]})
        
        # Start with a very early date.
        earliest_date = np.datetime64("1800-1-1")
        s = self.stocks
        symbs = self.stocks.keys()

        lengths = []
        
        # Find shortest stock array length.
        for symb in symbs:
            if earliest_date < s[symb].ratearray['date'][0]:
                earliest_date = s[symb].ratearray['date'][0]
                
        # Shorten rate and date data by lopping off the beginning dates to
        #     match the shortest dataset.
        for symb in symbs:
            sdate = s[symb].ratearray['date']
            if sdate[0]<earliest_date:
                idx = np.where(sdate==earliest_date)[0]
                s[symb].ratearray = s[symb].ratearray[idx:]
                s[symb].bencharray = s[symb].bencharray[idx:]
            lengths.append(len(s[symb].ratearray))
        
        # Check to see if all lengths are the same now...
        len_eq = np.array([lengths[i]==lengths[i+1] for i in range(len(lengths)-1)])
        if not np.all(len_eq):
            print "Missing data: imputing to calculate covariance"
            len_ary = np.array(lengths)
            max_len_idx = np.argmax(len_ary)
            max_symb = symbs[max_len_idx]
            newx = np.array([price_utils.adapt_datetime(dt) for dt in s[max_symb].ratearray['date'].tolist()])
            
            # Loop through symbols (again) to impute missing data
            for symb in symbs:
                
                x = np.array([price_utils.adapt_datetime(dt) for dt in s[symb].ratearray['date'].tolist()])
                y =s[symb].ratearray['rate']
                if len(x)<len(newx):
                    f = interp1d(x,y)
                    newy = f(newx)
                    newxdts = [price_utils.convert_datetime(dt) for dt in newx]
                    s[symb].ratearray = np.array(zip(newxdts, newy), dtype=dt_rates)

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
        
        for symb, stk_obj in self.stocks.iteritems():
            port_return += (stk_obj.annualized_adjusted_return * self.weights[symb])
            
        self.portfolio_return = port_return
            
        variance = self.calc_variance()
        return variance, port_return

    
    def calc_variance(self):
        """ A method for returning the portfolio variance.
        """
        
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
            
            TODO: Note: We currently allow leverage -- no limits on shorting
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
        
        # a change of weights according to 'a' will yeild a utility
        #     change as indicated below:
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
        print("Ending weights:\n%s\n" % self.port_opt.weights)
        print("Optimized Variance: %s and Portfolio Return: %s%%" % (variance, ret))
        
        
# EOF ####################################################################


