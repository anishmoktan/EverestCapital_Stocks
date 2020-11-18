import json
import requests
import os
import boto3 #to connect our information to AWS DynamoDB
from boto3.dynamodb.conditions import Attr
import bcrypt #library for cryting password

class Stock_Functions:
    
    def __init__(self):
        self.__Tablename__ = "EverestCapital_Stock_Portfolios"
        self.client = boto3.client('dynamodb')
        self.DB = boto3.resource('dynamodb')
        self.Primary_Column_Name = "Username"
        # self.Primary_key = 1
        self.columns = ["Cash", "Portfolio_Raw", "Portfolio_Updated", "ROI", "Total Networth"]   # providing values for the colmuns
        self.table = self.DB.Table(self.__Tablename__)

    def stock_price(stock_symbol):
        stock_symbol = stock_symbol.upper()
        base_url  = "https://www.alphavantage.co/query?"
        key = 1
        query_params = {"function": "TIME_SERIES_DAILY_ADJUSTED" , "symbol": stock_symbol, "apikey": key}
        try:
            response = requests.get(base_url, query_params)
            data = response.json()
            if response.status_code == 200:
                last_referesh = data['Meta Data']["3. Last Refreshed"]
                self.value= float(data["Time Series (Daily)"][last_referesh]["4. close"])
                return { "Message": "Successful",
                        "Market price" : self.value }
            elif response.status_code == 404:
                return { "Message": "404 error"}
        except KeyError:
            return { "Message": "Stock does not exist"}

    def purchase_stock(stock_symbol):
        stock_query = self.stock_price(stock_symbol)
        if stock_query[Message] == "Successful":


        
        #   if response.status_code == 200:
        #       print('\nWe were able to find the value of the stock!')
        #   elif response.status_code == 404:
        #       print('Sorry we could not find the stock you were looking for')
        #       return(self.search_stock)

    
      
      
  