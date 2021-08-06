import requests
import pandas as pd
from datetime import datetime
import math

sneaker_detail_url = "http://localhost:8080/api/sneakers/"

def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False
        
def post_all_sneakers(brandname):
    failed = 0
    df = pd.read_csv('../data/sneakers/adidas/yeezy/output.csv')
    for index, row in df.iterrows():
        url = row['url']
        brand_name = brandname
        style_name = row['name']
        image_path = row['image_path'][1:]

        retail_price = None
        if isnan(row['retail_price']) == False :
            retail_price = float(row['retail_price'][1:])

        # number_of_sale = 0
        # if math.isnan(float(row['number_of_sales'])) == False:
        #     number_of_sale = int(row['number_of_sales'])

        # average_sale_price = None
        # if isnan(row['average_sale_price']) == False:
        #     avgPrice = row['average_sale_price'].replace(',', '')
        #     average_sale_price = float(avgPrice[1:])
     
        style_code = row['style_code']
        colorway = row['colorway']
        ticker = row['ticker']
        datetime_obj=None
        if isnan(row['release_date']) == False:
            datetime_obj = datetime.strptime(row['release_date'], '%m/%d/%Y')
        payload = {
            'url':url,
            'brand_name': brand_name,
            'style_name': style_name,
            'image_path': image_path,
            'retail_price': retail_price,
            'style_code': style_code,
            'colorway': colorway,
            'ticker': ticker,
            'release_date': datetime_obj
        }
        res = requests.post(url=sneaker_detail_url, data = payload)
        print(res.status_code)
        if(res.status_code != 201):
            failed+=1
    print('Failed Post: ')
    print(failed) 
    print('Total Number of Trades: ')
    print(len(df))

def main():
    post_all_sneakers('Yeezy')

if __name__ == '__main__':
    main()