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
        
def post_all_ebay_sneaker_trades(brandname):
    failed = 0
    df = pd.read_csv('.\data\ebay\sneakers\YeezyBoost350V2BlackRed\page_1.csv')
    print(df.info)
    df.dropna(subset=['size'], inplace=True)
    print(df.info)
    # data = df.to_json(orient='index')
    # print(data)
    current_date = datetime.now()
    new_res = []
    for index, row in df.iterrows():

    #     print(row['name'])

        trade_date = None
        if row['sold_date'] != '':
            date_time = row['sold_date']
            trade_date = datetime.strptime(date_time, '%b %d, %Y')

        within_month = (current_date-trade_date)<=timedelta(7)

        new_res.append(trade_date)
    #     trade_name = ''
    #     if row['name'] != '' :
    #         trade_name = row['name']


    #     trade_size = ''
    #     if row['size'] != '':
    #         trade_size = row['size']
        
    #     trade_price = 0.0
    #     if row['price'] != '':
    #         price = row['price'].replace(',', '')
    #         trade_price = float(price[1:])
        
    #     payload = {
    #         'trade_name': trade_name,
    #         'ticker': ticker,
    #         'trade_date_time': trade_date,
    #         'trade_size': trade_size,
    #         'trade_price': trade_price
    #     }
        
    #     res = requests.post(url=sneaker_trades_url, data = payload)
    #     print(res.status_code)
    #     if(res.status_code != 200):
    #         failed+=1
    print(len(new_res))
    # print('Failed Post: ')
    # print(failed) 
    # print('Total Number of Trades: ')
    # print(len(df))

def main():
    post_all_ebay_sneaker_trades('Yeezy')

if __name__ == '__main__':
    main()