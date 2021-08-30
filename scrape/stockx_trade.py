
import requests
from pprint import pprint
import os
import csv
import time
from datetime import datetime
import pytz
from stockx_analysis import analyze_historical_data
HISTORICAL_TRADE_URL = "https://stockx.com/api/rest/v2/products/PRODUCT_UUID_PLACEHOLDER/activity?state=480&currency=USD&limit=250&page=1&sort=createdAt&order=DESC"
SNEAKER_URL = "http://localhost:8080/api/sneakers/"
INSERT_TRADE_URL = ' http://localhost:8080/api/stockx/'

HEADERS = {
    "Host": "stockx.com",
    "User-Agent": "PostmanRuntime/7.28.4"
}
cst = pytz.timezone('US/Central')
utc = pytz.utc

def convert_utc(date):
    utc_create = date
    utc_create = utc_create[0:19] + ' UTC+0000'
    utc_datetime = datetime.strptime(utc_create, "%Y-%m-%dT%H:%M:%S %Z%z")
    cst_datetime = utc_datetime.astimezone(cst)
    cst_datestr = cst_datetime.strftime("%Y-%m-%d")
    return cst_datestr

def fetch_historical_trade(product_id):
    historical_trade_url = HISTORICAL_TRADE_URL.replace("PRODUCT_UUID_PLACEHOLDER", product_id)
    
    trade_res = requests.get(url=historical_trade_url, headers=HEADERS)
    print(trade_res.status_code)
    if(trade_res.status_code != 200):
        print("sleep and then retry")
        time.sleep(15)
        return fetch_historical_trade(product_id)
    trades = trade_res.json()
    product_activity = trades['ProductActivity']
    for activity in product_activity:
        activity['createdAt_cst'] = convert_utc(activity['createdAt'])
    return trade_res.status_code, product_activity

def fetch_sneaker_info():
    res = requests.get(url=SNEAKER_URL)
    if(res.status_code == 200):
        return res.json()
    return []

def main():
    sneakers = fetch_sneaker_info()
    res_directory = "../data/trades/"
    if (not os.path.isdir("../data/trades/")):
        os.makedirs(res_directory, exist_ok=True)
    for index, sneaker in enumerate(sneakers):
        if(sneaker['product_id'] == '41dc590e-2339-43e9-af49-6fe8e93c9492'):
            failed = []
            # print(index)
            # print(sneaker['product_id'])
            # print(sneaker['title'])
            req = fetch_historical_trade(sneaker['product_id'])
            if req[0] == 200:
                analyze_historical_data(req[1], sneaker['product_id'])
            else:
                failed.append(sneaker['title'])
    print(failed)

if __name__ == '__main__':
    main()