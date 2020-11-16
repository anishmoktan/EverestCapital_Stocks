from flask import Flask, request
from EverestCapital_Stocks.StockFunctions import Search_Stock
search = Search_Stock()
app = Flask(__name__)


@app.route("/search-stock", methods=['POST'])
def search_stock():
    res = request.json
    stock_name = res["Stock_Name"]
    stock_price = search(stock_name)
    return stock_price
