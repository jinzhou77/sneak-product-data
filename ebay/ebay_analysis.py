import pandas as pd
from datetime import datetime, timedelta
import requests

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
INSERT_ANALYZE_URL = ' http://localhost:8080/api/analyze/'

def ebay_analyzer(trades, product_id):
    df = pd.DataFrame(trades)
    df = df[df['sold_date'] == CURRENT_DATE]
    average_all = df['sold_price'].mean()
    high_all = df['sold_price'].max()
    low_all = df['sold_price'].min()
    payload = {
        'product_id': product_id,
        'analyze_target_date': CURRENT_DATE,
        'size': 'All',
        'average_price':"{:.2f}".format(average_all) ,
        'high_price': "{:.2f}".format(high_all) ,
        'low_price': "{:.2f}".format(low_all),
        'number_of_trades': len(df),
        'platform': 'ebay',
        'publish_date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }
    print(payload)
    print("\n\n")
    # res = requests.post(url=INSERT_ANALYZE_URL, data=payload)
    # print("Status Code:", res.status_code)
    df = df.groupby(['size'])
    for name, group in df:
        size = name
        average = group['sold_price'].mean()
        max = group['sold_price'].max()
        min = group['sold_price'].min()
        payload = {
            'product_id': product_id,
            'analyze_target_date': CURRENT_DATE,
            'size': size,
            'average_price': "{:.2f}".format(average),
            'high_price': "{:.2f}".format(max) ,
            'low_price': "{:.2f}".format(min),
            'number_of_price': len(group),
            'platform': 'ebay',
            'publish_date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        print(payload)
        print("\n\n")
        # res = requests.post(url=INSERT_ANALYZE_URL, data = payload)
        # print(res.status_code)

    print("Analyze Finished")