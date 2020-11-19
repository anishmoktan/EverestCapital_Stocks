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
                return { "Message": "Successful",
                         "Market price": self.value,
                         "Date": last_referesh,
                         "Market data": data }
            elif response.status_code == 404:
                return { "Message": "404 error"}
        except KeyError:
            return { "Message": "Stock does not exist"}

    def purchase_stock(self, username, stock_symbol, quantity):

        stock_query = self.search_stock(stock_symbol)
        if stock_query[Message] == "Successful":

            response = self.table.scan(
                FilterExpression=Attr("username").eq(user)
            )
            if len(response["Items"]) > 0:

                cash = response["Items"][0]['Cash']
                portfolio = response["Items"][0]['Portfolio_Raw']
                updated_portfolio = response["Items"][0]['Portfolio_Updated']
                roi = response["Items"][0]['ROI']
                net_worth = response["Items"][0]['Total Networth']

                if (stock_query["Market price"] * quantity) > cash:
                    return { "Message": "Not enough cash for purchse"
                    }
                else:
                    cash = cash - (stock_query["Market price"] * quantity)

                    if stock_symbol in portfolio:
                        portfolio[stock_symbol][stock_query["Date"]] = [quantity,stock_query["Market price"]]




                        response = self.table.update_item( Key={
                        'username': username
                        },



                        UpdateExpression="set Cash=:a, Portfolio_Raw=:b, Portfolio_Updated=:c, ROI=:d, Total_Networth=:e",
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
                        portfolio[stock_symbol]= {stock_query["Date"]:[quantity,stock_query["Market price"]}

                

            else:
                return{
                    "Result": False,
                    "Error": "DB error",
                    "Description": "User info was not updated"
                }
        else:
            return { "Message": "Error with stock search"

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
