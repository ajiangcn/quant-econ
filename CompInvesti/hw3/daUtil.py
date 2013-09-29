import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

# get the historical price data
def getHistoricalPriceData(symbols, startDate, endDate):
	dt_timeofday = dt.timedelta(hours=16)
	dt_start = dt.datetime(startDate.year, startDate.month, startDate.day)
	dt_end = dt.datetime(endDate.year, endDate.month, endDate.day)
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
	ls_keys = ['open','high','low','close','volume','actual_close']

	c_dataobj = da.DataAccess('Yahoo')
	ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))
	return d_data
