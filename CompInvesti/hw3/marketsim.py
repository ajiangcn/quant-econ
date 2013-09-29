# import Enum support
# pass the parameters
# read the order to memory
import sys

class Order(object):
	"""docstring for Order"""
	def __init__(self, year, month, day, symbol, action, numOfShares):
		self.year = year
		self.month = month
		self.day = day
		self.symbol = symbol
		self.action = action
		self.numOfShares = numOfShares
	def __str__(self):
		# to string of the order object
		# year-month-day symbol trade numberOfShares
		return "%s-%s-%s %s %s %s"%(self.year,self.month,self.day,self.symbol,self.action,self.numOfShares)


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


# the function to load the orders from file and return a list of Order objects
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
		order = Order(fields[0],fields[1],fields[2],fields[3],fields[4],fields[5])
		result.append(order)
	# return results
	return result
		

# main function for the market simulation function
def main(argv):
	'''Main function'''
	intialBalance = argv[0]
	orderFile = argv[1]
	outputFile = argv[2]

	#load the orders to memory
	orderList = loadOrders(orderFile)
	

if __name__ == '__main__':
	# the first argument is the script file name
	main(sys.argv[1:])
