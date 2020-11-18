from flask import Flask, request
from EverestCapital_Stocks.StockFunctions import Search_Stock
search = Search_Stock()
app = Flask(__name__)


@app.route("/search-stock", methods=['POST']) #Shold show the historical graph with current price to buy 
def search_stock():
    res = request.json
    stock_name = res["Stock_Name"]
    stock_price = search(stock_name)
    return stock_price

@app.route("/buy-stock",methods=['POST']) #Should show the historical graph first and then trigger a purchase
def buy_stock():
    res = request.json
    stock_name = res["Stock_Name"]
    quantity = int(res["Quantity"])

    

    stock_price = search(stock_name)
    pass

@app.route("/sell-stock",methods=['POST']) #Should show the historical graph first and then trigger a sell
def sell_stock():
    res = request.json
    stock_name = res["Stock_Name"]
    stock_price = search(stock_name)
    pass

