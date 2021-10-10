import pandas as pd
import os 
from pprint import pprint
from datetime import datetime, timedelta
import requests
CURRENT_DATE = (datetime.now()-timedelta(1)).strftime("%Y-%m-%d")
INSERT_ANALYZE_URL = ' http://localhost:8080/api/analyze/'

def analyze_historical_data(hist_trades, product_id):
    payload = {}
    df = pd.DataFrame(hist_trades)
    df = df[df['createdAt_cst'] == CURRENT_DATE]
    average_all = df['localAmount'].mean()
    high_all = df['localAmount'].max()
    low_all = df['localAmount'].min()

    payload = {
        'product_id': product_id,
        'analyze_target_date': CURRENT_DATE,
        'size': 'All',
        'average_price':"{:.2f}".format(average_all) ,
        'high_price': "{:.2f}".format(high_all) ,
        'low_price': "{:.2f}".format(low_all),
        'number_of_trades': len(df),
        'platform': 'stockx',
        'publish_date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }
    res = requests.post(url=INSERT_ANALYZE_URL, data = payload)
    print("Status Code:", res.status_code)
    df = df.groupby(['shoeSize'])
    for name, group in df:
        size = name
        average = group['localAmount'].mean()
        max = group['localAmount'].max()
        min = group['localAmount'].min()
        payload = {
            'product_id': product_id,
            'analyze_target_date': CURRENT_DATE,
            'size': size,
            'average_price':"{:.2f}".format(average) ,
            'high_price': "{:.2f}".format(max) ,
            'low_price': "{:.2f}".format(min),
            'number_of_trades': len(group),
            'platform': 'stockx',
            'publish_date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        res = requests.post(url=INSERT_ANALYZE_URL, data = payload)
        print(res.status_code)
    print("\n\n")
