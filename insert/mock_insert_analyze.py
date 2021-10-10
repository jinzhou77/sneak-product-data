import requests
from datetime import datetime, timedelta
import random

INSERT_TRADE_URL = ' http://localhost:8080/api/analyze/'
CURRENT_DATE = datetime.now()
def main():
    payloads = []
    for i in range(30):
        payloads.append({
            'product_id': 'd290e592-2552-4a00-a705-3102caecc473',
            'analyze_target_date': (CURRENT_DATE+timedelta(i)).strftime("%Y-%m-%d"),
            'size': 'All',
            'average_price': str(random.randint(220,280)),
            'high_price': str(random.randint(220,280)),
            'low_price': str(random.randint(220,280)),
            'number_of_trades': random.randint(50,250),
            'publish_date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'platform': 'stockx'
        })
        payloads.append({
            'product_id': 'd290e592-2552-4a00-a705-3102caecc473',
            'analyze_target_date': (CURRENT_DATE+timedelta(i)).strftime("%Y-%m-%d"),
            'size': 'All',
            'average_price': str(random.randint(220,280)),
            'high_price': str(random.randint(220,280)),
            'low_price': str(random.randint(220,280)),
            'number_of_trades': random.randint(50,250),
            'publish_date': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'platform': 'ebay'
        })
    for payload in payloads:
        requests.post(url=INSERT_TRADE_URL, data=payload)
    
if __name__ == '__main__':
    main()