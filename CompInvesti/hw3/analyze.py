import sys
import math
import datetime as dt
import daUtil as dau
import numpy as np
import QSTK.qstkutil.qsdateutil as du

class Value(object):
	"""docstring fos Value"""
	def __init__(self, date, value):
		self.date = date
		self.value = value
	def __str__(self):
		return "%s %s"%(self.date, self.value)
	
# calculate the mean of the reutrn seq
def getMeanOfReturn(returns):
	return np.mean(returns)

# calculate the standard deviation of the return seq
def getStdOfReturn(returns):
	return np.std(returns)

# get the sharpe ratio of a value sequence
def getSharpeRatioOfValues(values):
	dailyReturns = getDailyReturnSeq(values)
	mean = getMeanOfReturn(dailyReturns)
	std = getStdOfReturn(dailyReturns)
	return math.sqrt(250)*mean/std


# calculate the total reutrn of the value sequence
# assume the value sequence is order by date
def getTotalReturn(values):
	beginningValue = values[0]
	endingValue = values[-1]
	return endingValue.value/beginningValue.value

# get daily return sequence without date information
def getDailyReturnSeq(values):
	result = []
	numOfPoints = len(values)
	for x in range(1, numOfPoints):
		#result.append(math.log1p(values[x].value/values[x-1].value-1.0))
		result.append(values[x].value/values[x-1].value-1.0)
	return result

# get the date range for the values
def getDateRange(values):
	startDate = values[0].date
	endDate = values[-1].date
	return (startDate, endDate)

# fetch the benchmark values
def getValueForSymbol(symbol, targetValues):
	dateRange = getDateRange(targetValues)
	startDate = dateRange[0]
	endDate = dateRange[1]
	adjustedEndDate = endDate + dt.timedelta(days=1)
	dau_data = dau.getHistoricalPriceData([symbol], startDate, adjustedEndDate)
	data = dau_data['close'][symbol]
	dateList = du.getNYSEdays(startDate, adjustedEndDate, dt.timedelta(hours=16))
	result = []
	for date in dateList:
		result.append(Value(dt.datetime(date.year, date.month, date.day), data.loc[date]))
	result.sort(key=lambda v: v.date)
	return result


# load date from portofolio values file
def loadValues(file):
	result = []
	with open(file, 'r') as f:
		read_data = f.read()
		lines = read_data.split('\n')
		for line in lines:
			if (line != ''):
				data = line.rstrip()
				fields = data.split(',')
				date = dt.datetime(int(fields[0]),int(fields[1]),int(fields[2]))
				value = float(fields[3])
				result.append(Value(date, value))
			else:
				# ignore the empty lines
				continue
	# return result
	result.sort(key=lambda v: v.date)
	return result

def main(argv):
	'''main function'''
	valuesFile = argv[0]
	benchmarkSym = argv[1]

	values = loadValues(valuesFile)
	benchmarkValues = getValueForSymbol(benchmarkSym, values)

	dateRange = getDateRange(values)

	print "The final value of the portofolio using the sample file is -- %s\n"%(values[-1].value)
	print "Details of the Performance of the portofolio : \n"
	print "Date Range: %s to %s\n"%(dateRange[0],dateRange[1])
	print "Sharpe Ratio of Fund : %s"%getSharpeRatioOfValues(values)
	print "Sharpe Ratio of %s : %s\n"%(benchmarkSym, getSharpeRatioOfValues(benchmarkValues))
	print "Total Return of Fund: %s"%getTotalReturn(values)
	print "Total Return of %s : %s\n"%(benchmarkSym, getTotalReturn(benchmarkValues))
	print "Standard Deviation of Fund : %s"%getStdOfReturn(getDailyReturnSeq(values))
	print "Standard Deviation of %s : %s\n"%(benchmarkSym, getStdOfReturn(getDailyReturnSeq(benchmarkValues)))
	print "Average Daily Return of Fund : %s"%getMeanOfReturn(getDailyReturnSeq(values))
	print "Average Daily Return of %s : %s"%(benchmarkSym, getMeanOfReturn(getDailyReturnSeq(benchmarkValues)))


if __name__ == '__main__':
	main(sys.argv[1:])