import requests
import pandas as pd
from datetime import datetime
import math
import numpy as np
from pprint import pprint

sneaker_detail_url = "http://localhost:8080/api/sneakers/"

def post_all_sneakers():
    success = 0
    df = pd.read_csv('../data/sneakers/result.csv', encoding = "ISO-8859-1")
    for i, row in enumerate(df.itertuples()):
        product_id = row.id
        brand = row.brand
        category = row.category
        shoe = row.shoe
        colorway = row.colorway
        gender = row.gender
        image_url = row.imageUrl
        thumb_url = row.thumbUrl
        release_date = row.releaseDate
        below_retail = row.belowRetail
        retail_price = row.retailPrice
        style_id = row.styleId
        ticker_symbol = row.tickerSymbol
        url_key = row.urlKey
        title = row.title
        market_annual_high = row.marketAnnualHigh
        market_annual_low = row.marketAnnualLow
        market_sales_last_72hours = row.marketSalesLast72Hours
        market_lowest_ask = row.marketLowestAsk
        market_lowest_ask_size = row.marketLowestAskSize
        market_highest_bid = row.marketHighestBid
        market_highest_bid_size = row.marketHighestBidSize

        payload = {
            'product_id': product_id,
            'brand':brand,
            'category':category,
            'shoe':shoe,
            'colorway':colorway,
            'gender':gender,
            'image_url':image_url,
            'thumb_url':thumb_url,
            'release_date':release_date,
            'below_retail':below_retail,
            'retail_price':float(retail_price),
            'style_id':style_id,
            'ticker_symbol':ticker_symbol,
            'url_key':url_key,
            'title':title,
            'market_annual_high':float(market_annual_high), 
            'market_annual_low':float(market_annual_low), 
            'market_sales_last_72hours':market_sales_last_72hours,
            'market_lowest_ask':float(market_lowest_ask), 
            'market_lowest_ask_size':market_lowest_ask_size,
            'market_highest_bid':float(market_highest_bid), 
            'market_highest_bid_size':market_highest_bid_size
        }
        
        res = requests.post(url=sneaker_detail_url, data = payload)
        print(res.status_code)
        if(res.status_code == 200 or res.status_code==201):
            success+=1
    return success

def main():
    success_posts = post_all_sneakers()
    print("Total Number of Sneakers:\n", success_posts)
    
    
if __name__ == '__main__':
    main()