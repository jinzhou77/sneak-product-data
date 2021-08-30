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
        productId = row.id
        brand = row.brand
        category = row.category
        shoe = row.shoe
        colorway = row.colorway
        gender = row.gender
        imageUrl = row.imageUrl
        thumbUrl = row.thumbUrl
        releaseDate = row.releaseDate
        belowRetail = row.belowRetail
        retailPrice = row.retailPrice
        styleId = row.styleId
        tickerSymbol = row.tickerSymbol
        urlKey = row.urlKey
        title = row.title
        marketAnnualHigh = row.marketAnnualHigh
        marketAnnualLow = row.marketAnnualLow
        marketSalesLast72Hours = row.marketSalesLast72Hours
        marketLowestAsk = row.marketLowestAsk
        marketLowestAskSize = row.marketLowestAskSize
        marketHighestBid = row.marketHighestBid
        marketHighestBidSize = row.marketHighestBidSize

        payload = {
            'productId': productId,
            'brand':brand,
            'category':category,
            'shoe':shoe,
            'colorway':colorway,
            'gender':gender,
            'imageUrl':imageUrl,
            'thumbUrl':thumbUrl,
            'releaseDate':releaseDate,
            'belowRetail':belowRetail,
            'retailPrice':float(retailPrice),
            'styleId':styleId,
            'tickerSymbol':tickerSymbol,
            'urlKey':urlKey,
            'title':title,
            'marketAnnualHigh':float(marketAnnualHigh), 
            'marketAnnualLow':float(marketAnnualLow), 
            'marketSalesLast72Hours':marketSalesLast72Hours,
            'marketLowestAsk':float(marketLowestAsk), 
            'marketLowestAskSize':marketLowestAskSize,
            'marketHighestBid':float(marketHighestBid), 
            'marketHighestBidSize':marketHighestBidSize
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