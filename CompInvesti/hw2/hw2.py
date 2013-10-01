'''
@author: Youjiang Wu
@contact: ajiangcn@gmail.com
@summary: Computational Investing home work 2
'''

import sys
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

def writeEventsToFile(file, events, symbols, timestamps):
    with open(file, 'wb') as f:
        count = 0
        for sym in symbols:
            for i in range(0,len(timestamps)):
                date = timestamps[i]
                if (events[sym].ix[date] == 1):
                    sellDate = timestamps[i+5]
                    # year, month, date, ticker, trade, 100
                    f.write("%s,%s,%s,%s,Buy,100\n"%(date.year,date.month,date.day,sym))
                    f.write("%s,%s,%s,%s,Sell,100\n"%(sellDate.year,sellDate.month,sellDate.day,sym))


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']
    event_count = 0
    
    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            # Event is found if yesterday's price is greater equal to 5
            # And today's price is less than 5.0
            if f_symprice_yest >= 5.0 and f_symprice_today < 5.0:
              df_events[s_sym].ix[ldt_timestamps[i]] = 1
              event_count += 1

    print ("Total event number is %s." %(event_count))
    return df_events


if __name__ == '__main__':
    orderFile = sys.argv[1]
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)
    writeEventsToFile(orderFile, df_events, ls_symbols, ldt_timestamps)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy0912.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
