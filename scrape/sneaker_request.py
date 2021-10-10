import requests
from pprint import pprint
import os
import csv

SNEAKER_URL  = "https://stockx.com/api/browse?_tags=TAG_PLACEHOLDER&productCategory=sneakers&gender=men&sort=most-active&order=DESC"
HISTORICAL_TRADE_URL = "https://stockx.com/api/rest/v2/products/PRODUCT_UUID_PLACEHOLDER/activity?state=480&currency=USD&sort=createdAt&order=DESC"
HEADERS = {
    "Host": "stockx.com",
    "User-Agent": "PostmanRuntime/7.28.4"
}

def fetch_most_popular_sneakers():
    brand_models = [
        {
            "brand": "air%20jordan",
            "models": ["one", "three", "four", "five", "six", "eleven", "twelve", "thirteen"]
        },
        {
            "brand": "adidas",
            "models": ['yeezy']
        },
        {
            "brand": "nike",
            "models": ["nike%20basketball", "air%20max", "air%20force", "kobe", "lebron"]
        }
    ]
    tag_pages = []
    for brand_model in brand_models:
        brand_name = brand_model['brand']
        for model in brand_model['models']:
            if model == 'one' or model=='yeezy' or model=='nike%20basketball':
                tag_pages.append({
                    'tag': model+','+brand_name,
                    'page': 0
                })
            else:
                tag_pages.append({
                    'tag': model+','+brand_name,
                    'page': 0
                })
    pprint(tag_pages)
    all_products = []
    for tag_page in tag_pages:
        sneaker_url = SNEAKER_URL.replace("TAG_PLACEHOLDER", tag_page['tag'])
        if tag_page['page'] == 0:
            res = requests.get(url=sneaker_url, headers=HEADERS)
            print("Send Request to:", sneaker_url)
            print("Response Code:", res.status_code)
            products = res.json()['Products']
            print("Product Length:", len(products))
            all_products = all_products + products
        else:
            index = 1
            products = []
            while(index<=tag_page['page']):
                sneaker_url = SNEAKER_URL.replace("TAG_PLACEHOLDER", tag_page['tag'])+ "&page="+str(index)
                res = requests.get(url=sneaker_url, headers=HEADERS)
                print("Send Request to:", sneaker_url)
                print("Response Code:", res.status_code)
                products = res.json()['Products']
                print("Product Length:", len(products))
                all_products = all_products + products
                index+=1
    print(len(all_products))
    output_product = []
    for product in all_products:
        output_product.append({
            'id': product['id'], 
            'brand': product['brand'],
            'category': product['category'], 
            'shoe': product['shoe'],
            'colorway': product['colorway'], 
            'gender': product['gender'], 
            'imageUrl': product['media']['imageUrl'],
            'thumbUrl': product['media']['thumbUrl'], 
            'releaseDate': product['releaseDate'], 
            'belowRetail': product['belowRetail'], 
            'retailPrice': product['retailPrice'], 
            'styleId': product['styleId'], 
            'tickerSymbol': product['tickerSymbol'], 
            'title': product['title'], 
            'urlKey': product['urlKey'], 
            'marketAnnualHigh': product['market']['annualHigh'],
            'marketAnnualLow':  product['market']['annualLow'],
            'marketSalesLast72Hours':  product['market']['salesLast72Hours'],
            'marketLowestAsk': product['market']['lowestAsk'],
            'marketLowestAskSize': product['market']['lowestAskSize'],
            'marketHighestBid': product['market']['highestBid'],
            'marketHighestBidSize': product['market']['highestBidSize'] 
        })
    res_directory = "../data/sneakers/"
    if (not os.path.isdir("../data/sneakers/")):
        os.makedirs(res_directory, exist_ok=True)
    save_dict_to_file(res_directory, output_product)
    return output_product

def save_dict_to_file(directory, page_dicts):
    with open(directory + "result.csv", 'w',  encoding="utf-8") as f:
        w = csv.DictWriter(f, page_dicts[0].keys())
        w.writeheader()
        w.writerows(page_dicts)

def main():
    sneakers = fetch_most_popular_sneakers()
    return 

if __name__ == '__main__':
    out = main()