from ib_insync import *
from pprint import pprint

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1, readonly=False)
ib.positions()

contract = Forex('AUDCHF')

print(contract)



data = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='30 D',
    barSizeSetting='1 hour',
    whatToShow='MIDPOINT',
    useRTH=True,
    formatDate=1,
)

pprint(data)

news = ib.reqHistoricalNews(10003, 8314, "BRFG", "", "", 10)

print(news)

# ib.reqMarketDataType(4)

# data = ib.reqMktData(contract)

ib.disconnect()
