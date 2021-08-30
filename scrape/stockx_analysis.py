import pandas as pd
import os 
from pprint import pprint
from datetime import datetime, timedelta
import requests
CURRENT_DATE = (datetime.now()-timedelta(1)).strftime("%Y-%m-%d")
INSERT_TRADE_URL = ' http://localhost:8080/api/stockx/'

def analyze_historical_data(hist_trades, product_id):
    payload = {}
    df = pd.DataFrame(hist_trades)
    df = df[df['createdAt_cst'] == CURRENT_DATE]
    # print(len(df))
    #get average of all the trades
    average_all = df['localAmount'].mean()
    high_all = df['localAmount'].max()
    low_all = df['localAmount'].min()
    # print(type(average_all))
    # print(type(high_all))
    # print(type(low_all))
    payload = {
        'product_id': product_id,
        'analyze_target_date': CURRENT_DATE,
        'size': 'All',
        'average_price':"{:.2f}".format(average_all) ,
        'high_price': "{:.2f}".format(high_all) ,
        'low_price': "{:.2f}".format(low_all),
        'number_of_trades': len(df),
        'publish_date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }
    res = requests.post(url=INSERT_TRADE_URL, data = payload)
    df = df.groupby(['shoeSize'])
    for name, group in df:
        size = name
        average = group['localAmount'].mean()
        max = group['localAmount'].max()
        min = group['localAmount'].min()
        # print('size:', size)
        # print('average:', average)
        # print('min:', min)
        # print('max:', max)
        # print('number of transactions:', len(group))
        payload = {
            'product_id': product_id,
            'analyze_target_date': CURRENT_DATE,
            'size': size,
            'average_price':"{:.2f}".format(average) ,
            'high_price': "{:.2f}".format(max) ,
            'low_price': "{:.2f}".format(min),
            'number_of_trades': len(group),
            'publish_date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        res = requests.post(url=INSERT_TRADE_URL, data = payload)
    print("\n\n")
