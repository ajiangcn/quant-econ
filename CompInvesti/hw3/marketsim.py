# import Enum support
# pass the parameters
# read the order to memory
import sys
import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

class Order(object):
	"""docstring for Order"""
	def __init__(self, date, symbol, action, numOfShares):
		self.date = date
		self.symbol = symbol
		self.action = action
		self.numOfShares = numOfShares
	def __str__(self):
		# to string of the order object
		# year-month-day symbol trade numberOfShares
		return "%s %s %s %s"%(self.date,self.symbol,self.action,self.numOfShares)

# equities is a dictinory of symbol to the number of shares
class Position(object):
	"""docstring fss Position"""
	def __init__(self, date, cash, equities):
		self.date = date
		self.cash = cash
		self.equities = equities
	def __str__(self):
		return "Date: %s The cash is %s, and the equities is %s."%(self.date, self.cash, self.equities)
	def setDate(self, date):
		self.date = date


class Trade(object):
	"""docstring for Trade type"""
	buy = 1
	sell = 2


class OrderFormatError(Exception):
	'''docstring for OrderFormatError'''
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


# translat the buy/sell action to enum
def getTradeAction(action):
	if (action.lower() == 'buy'):
		return Trade.buy
	if (action.lower() == 'sell'):
		return Trade.sell


# get all the symbols involved in the order list
def getAllSymbols(orderList):
	result = set()
	for order in orderList:
		result.add(order.symbol)
	resultList = list()
	for symbol in result:
		resultList.append(symbol)
	return resultList


# get the maximum time ranges for the involved order list
def getMaximumTimeRange(orderList):
	min = None
	max = None
	for order in orderList:
		if(min is None and max is None):
			min = order.date
			max = order.date
		else:
			if (order.date < min):
				min = order.date
			if (order.date > max):
				max = order.date
	#return results
	return (min, max)

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

# process the order which take a initial position, the order to be processed and the executed price
# return the position after the order
def processOrder(beginningPos, order, executed_price):
	# beginning position
	beginCash = beginningPos.cash
	accumulatedEquities = beginningPos.equities
	# executed order total
	executed_total = order.numOfShares * executed_price
	# individual equity position before the trade
	startEquity = accumulatedEquities[order.symbol]
	if (order.action == Trade.buy):
		# after position, adjust the cash and equities at the same time
		afterCash = beginCash - executed_total
		endEquity = startEquity + order.numOfShares
		accumulatedEquities[order.symbol] = endEquity
		endingPosition = Position(order.date, afterCash, accumulatedEquities)
		return endingPosition
	elif (order.action == Trade.sell):
		# after sell position
		afterCash = beginCash + executed_total
		endEquity = startEquity - order.numOfShares
		accumulatedEquities[order.symbol] = endEquity
		endingPosition = Position(order.date, afterCash, accumulatedEquities)
		return endingPosition
	else:
		raise Exception("Unsupported trade operation.")

# get the executed price for the order
def getExecutedPrice(order, data):
	dt_date = dt.datetime(order.date.year, order.date.month, order.date.day, 16)
	return data['actual_close'][order.symbol].loc[dt_date] 

# get the orders for a specified date
# the date passed in is added a time 16:00
# while the order list date doesn't have time information
def getOrdersForDate(date, orderList):
	result = []
	for order in orderList:
		dt_date = dt.datetime(order.date.year, order.date.month, order.date.day, 16)
		if (dt_date == date):
			result.append(order)
	#return result
	return result

# get the equity's actual close price for a given date
def getEquityPriceForDate(symbol, date, data):
	return data['actual_close'][symbol].loc[date]

# calculate the value of a given position
def getPositionVaue(pos, data):
	cash = pos.cash
	date = pos.date
	accumulatedEquityValue = 0.0
	for symbol in pos.equities.keys():
		shares = pos.equities[symbol]
		equityPrice = getEquityPriceForDate(symbol, date, data)
		accumulatedEquityValue += shares * equityPrice
	# total value is cash plus equity value at that date
	return cash + accumulatedEquityValue


# the function to load the orders from file and return a list of Order objects
# the order is sorted by order date in ascending order
def loadOrders(file):
	result = []
	f = open(file, "r")
	data = f.read().replace('\r','\n')
	f.close
	for line in data.split('\n'):
		# remove the trailing comma
		lineData = line.rstrip(',')
		# ignore the empty line
		if (lineData == ''): continue
		fields = lineData.split(',')
		if (len(fields) != 6):
			raise OrderFormatError("Order format error: %s" % lineData)
		orderDate = dt.date(int(fields[0]),int(fields[1]),int(fields[2]))
		order = Order(orderDate,fields[3],getTradeAction(fields[4]),int(fields[5]))
		result.append(order)
	# sort the order by date
	result.sort(key=lambda order: order.date)
	# return result
	return result
		

# main function for the market simulation function
def main(argv):
	'''Main function'''
	intialBalance = argv[0]
	orderFile = argv[1]
	outputFile = argv[2]

	#load the orders to memory
	orderList = loadOrders(orderFile)

	#get all symbols involved
	allSymbols = getAllSymbols(orderList)

	#get the maximum time range involved in the orders
	dateRange = getMaximumTimeRange(orderList)
	startDate = dateRange[0]
	endDate = dateRange[1]
	adjustedEndDate = endDate + dt.timedelta(days=1)
	
	#fetch the historical price data for all the symbols in the maximux date range
	price_data = getHistoricalPriceData(allSymbols, startDate, adjustedEndDate)

	# beginning position
	beginningEquities = dict()
	for symbol in allSymbols:
		beginningEquities[symbol] = 0
	beginningPos = Position(startDate, 1000000.0, beginningEquities)
	accumulatedPos = beginningPos

	# simulate the orders, open the output file and writ the daily balance to the outputfile
	with open(outputFile, 'wb') as f:
		# dateList = [startDate + dt.timedelta(days=x) for x in range (0, numDays)]
		# only get the trading days
		dateList = du.getNYSEdays(startDate, endDate, dt.timedelta(hours=16))
		for date in dateList:
			orders = getOrdersForDate(date, orderList)
			if (len(orders) > 0):
				for order in orders:
					executed_price = getExecutedPrice(order, price_data)
					accumulatedPos = processOrder(accumulatedPos, order, executed_price)
					accumulatedPos.setDate(date)
					positionValue = getPositionVaue(accumulatedPos, price_data)
					f.write("%s,%s,%s,%s\n"%(date.year,date.month,date.day,positionValue))
			else:
				# if there is no order to process, still update the date of accumulated position
				accumulatedPos.setDate(date)
				positionValue = getPositionVaue(accumulatedPos, price_data)
				f.write("%s,%s,%s,%s\n"%(date.year,date.month,date.day,positionValue))


if __name__ == '__main__':
	# the first argument is the script file name
	main(sys.argv[1:])
