import requests
import pandas as pd
from datetime import datetime, timedelta, date
import math
import time 

sneaker_trades_url = "http://localhost:8080/api/trades/"

def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False
        
def post_all_sneaker_trades(brandname):
    failed = 0
    df = pd.read_csv('../data/stockX/sneakers/adidas/yeezy/AD-YB350V2CBR.csv') 
    df = df[df['name'] == 'adidas Yeezy Boost 350 V2 Black Red (2017/2020)']
    df.dropna(subset=['name'], inplace=True)
    for index, row in df.iterrows():
        
        nan_name = isnan(row['name'])
        nan_ticker = isnan(row['ticker'])
        nan_date = isnan(row['date'])
        nan_time = isnan(row['time'])
        nan_size = isnan(row['size'])
        nan_price = isnan(row['price'])
        if nan_name==False and nan_ticker==False and nan_date==False and nan_time==False and nan_size==False and nan_price==False:
            print(row['name'])

            trade_date = None
            if row['date'] != '':
                date_time = row['date']+ ', ' +row['time'][:-3]+':00'
                trade_date = datetime.strptime(date_time, '%A, %B %d, %Y, %I:%M %p :%S')

            trade_name = ''
            if row['name'] != '' :
                trade_name = row['name']
                
            ticker = ''
            if row['ticker'] != '':
                ticker = row['ticker']

            trade_size = ''
            if row['size'] != '':
                trade_size = row['size']
            
            trade_price = 0.0
            if row['price'] != '':
                price = row['price'].replace(',', '')
                trade_price = float(price[1:])
            
            payload = {
                'trade_name': trade_name,
                'ticker': ticker,
                'trade_date_time': trade_date,
                'trade_size': trade_size,
                'trade_price': trade_price
            }
            
            res = requests.post(url=sneaker_trades_url, data = payload)
            print(res.status_code)
            if(res.status_code != 200):
                failed+=1
    print('Failed Post: ')
    print(failed) 
    print('Total Number of Trades: ')
    print(len(df))

def main():
    post_all_sneaker_trades('Yeezy')

if __name__ == '__main__':
    main()