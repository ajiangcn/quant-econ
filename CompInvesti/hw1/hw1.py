'''
Home work 1 to write a simulate function which have thw following input/output
input:start date
      end date
      symbols for equities
      allocations to the equities at the beginning of the period
output: standard deviation of the daily return of the portfolio
        avarage daily return of the portfolio
        sharpe ratio of the portfolio
        cumulative return of the portfolio
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third party imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate(startDate, endDate, symbols, allocations):
    '''Home work 1, simulate function'''
    
    #Fetch the historical data
    dt_timeofday = dt.timedelta(hours=16)
    #Get a list of trading days between the start and end date
    ldt_timestamps = du.getNYSEdays(startDate, endDate, dt_timeofday)

    #create an object to access data from Yahoo
    #c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    c_dataobj = da.DataAccess('Yahoo')
    #keys to be read from the data
    ls_keys = ['open','high','low','close','volume','actual_close']
    #reading the data
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    #divide the close price with base price to get cumulative return
    d_adjClose = d_data['close'].values
    print d_adjClose
    d_basePrice = d_adjClose[0,]
    d_cumReturn = np.divide(d_adjClose, d_basePrice)
    print d_cumReturn
    d_portCumReturn = np.dot(d_cumReturn,allocations)
    
    #assume the original total investment is unit 1,calculat the daily return of the portfolio
    # d_0_data denote the portfolio daily return from day zero to sedond last day
    d_0_data = d_portCumReturn[0:len(d_portCumReturn)-1]
    # d_1_data denote the portfolio daily return from day 1 to last day
    d_1_data = d_portCumReturn[1:len(d_portCumReturn)] 
    d_portDailyReturn = np.subtract(np.divide(d_1_data, d_0_data),1.0) 
    # mean of the portfolio daily return
    d_port_mean = np.mean(d_portDailyReturn)
    d_port_std = np.std(d_portDailyReturn)
    d_port_sharpeRatio = np.sqrt(252) * d_port_mean / d_port_std
    # last element of portfolio cumulative return is the cumulative for the whole period
    d_port_cumReturn = d_portCumReturn[len(d_portCumReturn)-1]

    #print out the result
    print 'Start Date:', startDate.strftime("%B %d, %Y")
    print 'End Date:', endDate.strftime("%B %d, %Y")
    print 'Symbols:', symbols
    print 'Optimal Allocations:', allocations
    print 'Sharpe Ratio:', d_port_sharpeRatio
    print 'Volatility (stdev of daily returns):', d_port_std
    print 'Average Daily Return:', d_port_mean
    print 'Cumulative Return:', d_port_cumReturn
    return d_port_std,d_port_mean,d_port_sharpeRatio,d_port_cumReturn

def drange(start, stop, step):
    while start <= stop:
        yield start
        start += step

def optimize(startDate, endDate, symbols):
   bestPortfolio = [0,0,0,0]
   bestSharpeRatio = 0.0
   '''optimize the portfolio'''
   for x in drange(0,1.0, 0.1):
     for y in drange(0,1.0, 0.1):
       for z in drange(0,1.0, 0.1):
         for zz in drange(0,1.0, 0.1):
           if (x+y+z+zz) == 1.0:
             vol, daily_ret, sharpe, cum_ret = simulate(startDate, endDate, symbols, [x,y,z,zz])
             if sharpe > bestSharpeRatio:
               bestSharpeRatio = sharpe 
               bestPortfolio = [x,y,z,zz]
   return bestPortfolio,bestSharpeRatio
 
if __name__ == '__main__':
    simulate(dt.datetime(2011,1,1), dt.datetime(2011,12,31),["AAPL","GLD","GOOG","XOM"], [0.4,0.4,0.0,0.2])
    #simulate(dt.datetime(2010,1,1), dt.datetime(2010,12,31),["AXP","HPQ","IBM","HNZ"], [0.0,0.0,0.0,1.0])
    #bestAllocations,bestSharpeRatio=optimize(dt.datetime(2010,1,1),dt.datetime(2010,12,31),["AAPL","GOOG","IBM","MSFT"])
    #bestAllocations,bestSharpeRatio=optimize(dt.datetime(2010,1,1),dt.datetime(2010,12,31),["BRCM","TXN","IBM","HNZ"])
    #print bestAllocations,bestSharpeRatio
