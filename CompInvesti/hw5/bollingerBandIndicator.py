import sys
sys.path.append('/home/ajiangcn/github/quant-econ/CompInvesti/hw3')
import datetime as dt
import daUtil as dau
import pandas as pd
import matplotlib.pyplot as plt
import QSTK.qstkutil.qsdateutil as du

def calculateBDIndicators(sd, ed, ticker, period):
	tickers = list()
	tickers.append(ticker)
	d_data = dau.getHistoricalPriceData(tickers,sd, ed)
	closePrice = d_data['actual_close'][ticker]
	mid = pd.rolling_mean(closePrice, 20)
	std = pd.rolling_std(closePrice, 20)
	bollinger_val = (closePrice - mid)/std
	upperBound = closePrice + std
	lowerBound = closePrice - std
	return (upperBound, mid, lowerBound, closePrice, bollinger_val)

def main(argv):
	startDate = dt.datetime(2010,1,1)
	endDate = dt.datetime(2010,12,31)
	ticker = argv[0]
	period = argv[1]
	bdIndicators = calculateBDIndicators(startDate, endDate, ticker, period)
	upperBound = bdIndicators[0]
	mid = bdIndicators[1]
	lowerBound = bdIndicators[2]
	price = bdIndicators[3]
	bdVal = bdIndicators[4]

	dt_timeofday = dt.timedelta(hours=16)
	dt_timestamps = du.getNYSEdays(startDate, endDate, dt_timeofday) 
	# plot the graph
	plt.clf()
	plt.plot(dt_timestamps, price)
	plt.plot(dt_timestamps, mid)
	plt.plot(dt_timestamps, upperBound)
	plt.plot(dt_timestamps, lowerBound)
	plt.xlabel('Date')
	plt.ylabel('Adjusted Close')
	plt.legend(['Price','Mid', 'Upper', 'Lower'])
	plt.savefig('fig1.pdf', format='pdf')
	# plot the bollinger band values
	plt.clf()
	plt.plot(dt_timestamps, bdVal)
	plt.xlabel('Date')
	plt.ylabel('Bollinger Band Value')
	plt.savefig('fig2.pdf', format='pdf')
	print bdVal.loc[dt.datetime(2010,6,23,16)]


if __name__ == '__main__':
	main(sys.argv[1:])