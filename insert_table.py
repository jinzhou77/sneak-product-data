import requests
import pandas as pd
from datetime import datetime
import math

sneaker_detail_url = "http://127.0.0.1:8080/api/sneakers/"

def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False
        
def post_all_sneakers(brandname):
    df = pd.read_csv('./data/sneakers/adidas/yeezy/output.csv')
    for index, row in df.iterrows():
        url = row['url']
        brandname = brandname
        stylename = row['name']
        imagepath = row['image_path']

        retailprice = None
        if isnan(row['retail_price']) == False :
            retailprice = float(row['retail_price'][1:])

        numberofsale = 0
        if math.isnan(float(row['number_of_sales'])) == False:
            numberofsale = int(row['number_of_sales'])

        averagesaleprice = None
        if isnan(row['average_sale_price']) == False:
            avgPrice = row['average_sale_price'].replace(',', '')
            averagesaleprice = float(avgPrice[1:])
     
        stylecode = row['style_code']
        colorway = row['colorway']
        ticker = row['ticker']
        datetime_obj=None
        if isnan(row['release_date']) == False:
            datetime_obj = datetime.strptime(row['release_date'], '%m/%d/%Y')
        payload = {
            'url':url,
            'brandname': brandname,
            'stylename': stylename,
            'imagepath': imagepath,
            'retailprice': retailprice,
            'numberofsale': numberofsale,
            'averagesaleprice': averagesaleprice,
            'stylecode': stylecode,
            'colorway': colorway,
            'ticker': ticker,
            'releasedate': datetime_obj
        }
        res = requests.post(url=sneaker_detail_url, data = payload)
        print(res.status_code)
    print(len(df))

def main():
    post_all_sneakers('Yeezy')

if __name__ == '__main__':
    main()