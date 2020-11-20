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
        self.columns = ["Cash", "Portfolio_Raw", "Portfolio_Updated", "ROI", "Total_Networth"]   # providing values for the colmuns
        self.table = self.DB.Table(self.__Tablename__)

    def initiate_account(self, username): #Needs to  be triggered to give user default money

        if (self.account_exists(username)):
            return {
                "Result": False,
                "Message" : "Account already in the DB so using present account data"
            }

        else:
            response = self.table.put_item(
                Item={
                    self.Primary_Column_Name: username,
                    self.columns[0]: 10000,
                    self.columns[1]: {},
                    self.columns[2]: {},
                    self.columns[3]: 0,
                    self.columns[4]: 10000
                }
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return {
                    "Result": True,
                    "Error": None,
                    "Message": "User's stock DB was created succesfully",
                }
            else:
                return  {
                    "Result": False,
                    "Error": "Database error",
                    "Message": "Database error, account not in the initial DB"
                }

    def account_exists(self,username):
        response = self.table.scan(
            FilterExpression=Attr("Username").eq(username)
        )
        if reponse["Items"]:
            return True
        else:
            return False

    def authinticate_user(self,username):

        response = self.table.scan(
            FilterExpression=Attr("Username").eq(username)
        )

        if (len(response["Items"]) > 0):
            return {

                "Result" : True,
                "Error" : None,
                "Cash" : response['Items'][0]["Cash"],
                "Portfolio_Raw" : response['Items'][0]["Portfolio_Raw"],
                "Portfolio_Updated" : response['Items'][0]["Portfolio_Updated"],
                "ROI" : response['Items'][0]["ROI"],
                "Total_Networth" : response['Items'][0]["Total_Networth"]
            }
        else:
            return {
                "Result" : False,
                "Error" : "Username not found"
            }


    def search_stock(self, stock_symbol):
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
                return {
                         "Result": True,
                         "Message": "Successful",
                         "Market_price": self.value,
                         "Date": last_referesh,
                         "Market_data": data }
            elif response.status_code == 404:
                return { "Result": False,
                         "Message": "404 error"}
        except KeyError:
            return {
                "Result" : False,
                "Message": "Stock does not exist"}

    def purchase_stock(self, username, stock_symbol, quantity):

        stock_query = self.search_stock(stock_symbol)
        
        if stock_query['Result']:
            
            response = self.table.scan(
                FilterExpression=Attr("Username").eq(username)
            )
            if response["Items"]:
            
                Cash = response["Items"][0]['Cash']
                Portfolio_Raw = response["Items"][0]['Portfolio_Raw']
                Portfolio_Updated = response["Items"][0]['Portfolio_Updated']
                ROI = response["Items"][0]['ROI']
                Total_Networth = response["Items"][0]['Total_Networth']

                if (stock_query["Market price"] * quantity) > cash:
                    return { "Result": False,
                        "Message": "Not enough cash for purchse"
                    }
                else:
                    Cash = Cash - (stock_query["Market_price"] * quantity)

                    if stock_symbol in Portfolio_Raw:

                        inside = Portfolio_Raw[stock_symbol]
                        inside[stock_query["Date"]] = [quantity,stock_query["Market_price"]]

                        Portfolio_Updated = self.update_portfolio(portfolio_raw,stock_query["Date"])

                        roi_query = self.roi(Portfolio_Raw,Portfolio_Updated)
                        ROI = roi_query["ROI"]

                        Total_Networth = Cash + roi_query["Updated_Total"]

                        res = self.table.update_item(
                            key={'Username': username},
                            UpdateExpression = "set Cash=:a, Portfolio_Raw=:b, Portfolio_Updated=:c, ROI=:d, Total_Networth=:e",
                            ExpressionAttributeValues={
                            # ':n': New_BlogName,
                                ':a': Cash,
                                ':b': Portfolio_Raw,
                                ':c': Portfolio_Updated,
                                ':d': ROI,
                                ':e': Total_Networth
                                }
                        )

                        if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
                        return {
                            "Result": True,
                            "Error": None,
                            "Description": "Database was updated successfully",
                        }
                        else:
                            return {
                                "Result": False,
                                "Error": "Database error",
                                "Description": "Database error",
                            }


                    else:

                        Portfolio_Raw[stock_symbol]= {stock_query["Date"]:[quantity,stock_query["Market price"]}

                        Portfolio_Updated = self.update_portfolio(Portfolio_Raw,stock_query["Date"])

                        roi_query = self.roi(Portfolio_Raw,Portfolio_Updated)
                        ROI = roi_query["ROI"]

                        Total_Networth = Cash + roi_query["Updated_Total"]

                        res = self.table.update_item(
                            key={'Username': username},
                            UpdateExpression = "set Cash=:a, Portfolio_Raw=:b, Portfolio_Updated=:c, ROI=:d, Total_Networth=:e",
                            ExpressionAttributeValues={
                            # ':n': New_BlogName,
                                ':a': Cash,
                                ':b': Portfolio_Raw,
                                ':c': Portfolio_Updated,
                                ':d': ROI,
                                ':e': Total_Networth
                                }
                        )

                        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                        return {
                            "Result": True,
                            "Error": None,
                            "Description": "Database was updated successfully",
                        }
                        else:
                            return {
                                "Result": False,
                                "Error": "Database error",
                                "Description": "Database error",
                            }


            else:
                return{
                    "Result": False,
                    "Error": "DB error",
                    "Description": "User info was not updated"
                }
        else:
            return {
                "Message": "Error with stock search"
                }
    
    def update_portfolio(self,raw_portfolio,date_today):
        updated_port={}
        for stock in raw_portfolio:
            access = raw_portfolio[stock]
            quant=0
        
            for date in access:
                quant = quant + access[date][0]

            updated_port[stock]= {date_today:[quant,self.search_stock(stock)["Market_price"]]}

        return updated_port

    def roi(raw_port,updated_port):
        total_raw_worth= 0
        total_updated_worth = 0

        for stock in raw_port:
            for date in raw_port[stock]:
            total_raw_worth= total_raw_worth +raw_port[stock][date][0] * raw_port[stock][date][1]
        for stock in updated_port:
            for date in updated_port[stock]:
            total_updated_worth= total_updated_worth +updated_port[stock][date][0] * updated_port[stock][date][1]
  
        return
        { 
            "Raw_Total" : total_raw_worth,
            "Updated_Total" : total_updated_worth,
            "ROI" : (total_updated_worth-total_raw_worth)/total_raw_worth
            }





    def sell_stock(self,stock_symbol):
        stock_query = self.stock_price(stock_symbol)
        if stock_query[Message] == "Successful":

        #   if response.status_code == 200:
        #       print('\nWe were able to find the value of the stock!')
        #   elif response.status_code == 404:
        #       print('Sorry we could not find the stock you were looking for')
        #       return(self.search_stock)
    


    #For solving calculations:
    #  port= { 'AAPL':{"2020-11-17":[2,150],"2020-11-16":[3,160]} }

    # access=port['AAPL']
    # for i in access:
    # print(access[i][0]*access[i][1])
