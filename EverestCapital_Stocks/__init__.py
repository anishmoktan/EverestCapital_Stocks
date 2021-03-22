from flask import Flask, request
from EverestCapital_Stocks.StockFunctions import Stock_Functions
search = Stock_Functions()
app = Flask(__name__)

@app.route("/initiate-account", methods=['POST']) #Shold show the historical graph with current price to buy 
def search_stock():
    res = request.json
    username = res["Username"]
    initiate = search.initiate_account(username)
    return initiate

@app.route("/activate-account", methods=['POST']) #Shold show the historical graph with current price to buy 
def search_stock():
    res = request.json
    username = res["Username"]
    authenticate = search.authenticate_account(username)
    return authenticate

@app.route("/search-stock", methods=['POST']) #Shold show the historical graph with current price to buy 
def search_stock():
    res = request.json
    stock_name = res["Stock_Name"]
    stock_price = search.search_stock(stock_name)
    return stock_price

@app.route("/buy-stock",methods=['POST']) #Should show the historical graph first and then trigger a purchase
def buy_stock():
    res = request.json
    stock_name = res["Stock_Name"]
    quantity = int(res["Quantity"])
    purchase = search.purchase_stock(stock_symbol)
    return purchase

@app.route("/sell-stock",methods=['POST']) #Should show the historical graph first and then trigger a sell
def sell_stock():
    res = request.json
    stock_name = res["Stock_Name"]
    stock_price = search(stock_name)
    pass