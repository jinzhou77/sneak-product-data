import requests
import pandas as pd
from datetime import datetime
import math
import numpy as np

sneaker_detail_url = "http://localhost:8080/api/sneakers/"
failed = 0
  
def post_all_sneakers(brand_name, model_name):
    
    df = pd.read_csv('../data/sneakers/'+ brand_name + '/' + model_name + '/result.csv', encoding = "ISO-8859-1")
    df = df.replace(np.nan, 'N/A', regex=True)
    for index, row in df.iterrows():
        
        url = row['url']
        if(brand_name=='retrojordans'):
            brand_name="Air Jordan"
            
        model_name = model_name.replace("-", " ")    
        
        style_name = row['name']

        number_sales_72_hours = 0
        if row['sales_last_72'] != 'N/A':
            #  numberOfSale72Hours = row['sales_last_72'].replace(',', '')
             number_sales_72_hours = int(row['sales_last_72'])
        
        ticker = row['ticker']
        
        image_path = row['image_path']
        
        datetime_obj=None
        if row['release_date'] != 'N/A':
            datetime_obj = datetime.strptime(row['release_date'], '%m/%d/%Y')
            
        retail_price = None
        if row['retail_price'] != 'N/A':
            retailPrice = row['retail_price'].replace(',', '')
            retail_price = float(retailPrice[1:])

        style_code = row['style_code']
        
        colorway = row['colorway']
        
        number_sales_12_months = 0
        if row['number_of_sales'] != 'N/A':
            number_sales_12_months = int(row['number_of_sales'])

        price_premium = row['price_premium']
        
        average_sales_price = None
        if row['average_sale_price'] != 'N/A':
            avgPrice = row['average_sale_price'].replace(',', '')
            average_sales_price = float(avgPrice[1:])
        
        payload = {
            'url':url,
            'brand_name': brand_name,
            'model_name': model_name,
            'style_name': style_name,
            'number_sales_72_hours':number_sales_72_hours,
            'ticker': ticker,
            'image_path': image_path,
            'release_date': datetime_obj,
            'retail_price': retail_price,
            'style_code': style_code,
            'colorway': colorway,
            'number_sales_12_months': number_sales_12_months,
            'price_premium': price_premium,
            'average_sales_price': average_sales_price,
        }
        res = requests.post(url=sneaker_detail_url, data = payload)
        print(res.status_code)
        if(res.status_code != 201):
            global failed
            failed+=1
            print(brand_name)
            print(model_name)
            print(style_name)
    return len(df)

def main():
    map = {
        'retrojordans': ['air-jordan-1','air-jordan-3','air-jordan-4','air-jordan-5','air-jordan-6','air-jordan-7','air-jordan-9','air-jordan-11','air-jordan-12','air-jordan-13'],
        'adidas': ['yeezy', 'nmd', 'ultra-boost'],
        'nike': ['air-force', 'air-max', 'basketball', 'kd', 'kobe', 'lebron']
    }
    number_of_records = 0
    for brand, models in map.items():
        for model in models:
            df_length = post_all_sneakers(brand, model)
            number_of_records+=df_length
    print("Total Number of Sneakers:\n", number_of_records)
    print("Number of Failed Insert:\n", failed)
    
    
if __name__ == '__main__':
    main()