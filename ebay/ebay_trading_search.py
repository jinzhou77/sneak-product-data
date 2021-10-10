import os
from requests.models import HTTPError

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options

import time
import numpy as np
from datetime import datetime, timedelta
from pprint import pprint

import csv

import requests

from ebay_validation import ebay_validation
from ebay_analysis import ebay_analyzer

from random import randint

THRESHOLD = 60

TOLERANCE = 1

num_opened = 0

def trade_page_error(driver):
    error_page = False
    try:
        driver.find_element_by_xpath("//p[contains(text(), 'We looked everywhere.')]")
        print("Trade Page Not Found")
        error_page = True
    except NoSuchElementException:
        try:
            driver.find_element_by_xpath("//div[contains(@class, 'page-alert')]")
            print("Trade Page Error")
            error_page = True
        except NoSuchElementException:
            error_page = False
    return error_page

def get_shoe_trading_data(driver, sneaker_name, info_dict, product_id):
    outputs = []
    
    open_link(driver,info_dict['href_link'])

    if trade_page_error(driver) == False:
        print("Get Trade Data")
        index = info_dict['href_link'].find("epid")
        if info_dict['href_link'][index:] not in driver.current_url:
            print("URL did not match, Redirect to the right url")
            real_link = driver.find_element_by_xpath('//div[contains(@class, "nodestar-item-card-details__image-table")]/a/div/img')
            ActionChains(driver).click(real_link).perform()
            time.sleep(5)
    
        purchaseHistURL = "https://www.ebay.com/bin/purchaseHistory?item="
        seller = driver.find_element_by_xpath("//div[contains(@class, 'mbg')]/a/span").text
        condition = driver.find_element_by_xpath("//div[contains(@id, 'vi-itm-cond')]").text
        ship_fee = driver.find_element_by_xpath("//span[contains(@id, 'fshippingCost')]").text
        try:
            #Check if the list if available.
            driver.find_element_by_xpath("//a[contains(@class, 'vi-txt-underline')]")
            print("Purchase List Exist, redirect to the table page")
            try:
                shoe_size = driver.find_element_by_xpath("//td[contains(text(), 'US Shoe Size')]/following-sibling::td").text
            except NoSuchElementException:
                print("Shoe Size element does not exist")
                shoe_size = ''

            itemNumber = driver.find_element_by_xpath("//div[contains(@id, 'descItemNumber')]").text
            purchaseHistURL = purchaseHistURL + str(itemNumber)
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            open_link(driver,purchaseHistURL)
            table = driver.find_element_by_xpath("//table[contains(@class, 'app-table__table')]")
            rows = []
            print('Found the table')
            for row in table.find_elements_by_xpath(".//tr[contains(@class, 'app-table__row')]"):
                row_info = [td.text for td in row.find_elements_by_tag_name("td")]
                rows.append(row_info)
            for i, row in enumerate(rows):
                if(len(rows[i]) == 5):
                    sold_date_arr =  rows[i][4].split("at")
                    date_obj = datetime.strptime(sold_date_arr[0], "%d %b %Y ")
                    date_str = datetime.strftime(date_obj, "%b %d, %Y")
                    outputs.append({
                        'sneaker_id': product_id,
                        'name': sneaker_name,
                        'title': info_dict['sold_title'],
                        'seller': seller,
                        'trade_url': info_dict['href_link'],
                        'condition': condition,
                        'ship_fee': ship_fee.replace("$", ""),
                        'size': rows[i][1].replace("US Shoe Size: ", "").replace("US Shoe Size (Men's): ", ""),
                        'sold_price':  rows[i][2].replace("US $", ""),
                        'sold_date': datetime.strptime(date_str, "%b %d, %Y").strftime("%Y-%m-%d")
                    })
                else:
                    sold_date_arr =  rows[i][3].split("at")
                    date_obj = datetime.strptime(sold_date_arr[0], "%d %b %Y ")
                    date_str = datetime.strftime(date_obj, "%b %d, %Y")
                    outputs.append({
                        'sneaker_id': product_id,
                        'name': sneaker_name,
                        'title': info_dict['sold_title'],
                        'seller': seller,
                        'trade_url': info_dict['href_link'],
                        'condition': condition,
                        'ship_fee': ship_fee.replace("$", ""),
                        'size': shoe_size.replace("US Shoe Size: ", "").replace("US Shoe Size (Men's): ", ""),
                        'sold_price':  rows[i][1].replace("US $", ""),
                        'sold_date': datetime.strptime(date_str, "%b %d, %Y").strftime("%Y-%m-%d")
                    })
        except NoSuchElementException:
            print("Purchase List does not exist, find the data in this page")
            shoe_size = driver.find_element_by_xpath("//td[contains(text(), 'US Shoe Size')]/following-sibling::td").text
            outputs.append({
                'sneaker_id': product_id,
                'name': sneaker_name,
                'title': info_dict['sold_title'],
                'seller': seller,
                'trade_url': info_dict['href_link'],
                'condition': condition,
                'ship_fee': ship_fee.replace("$", ""),
                'size': shoe_size.replace("US Shoe Size: ", "").replace("US Shoe Size (Men's): ", ""),
                'sold_price':  info_dict['sold_price'],
                'sold_date': datetime.strptime(info_dict['sold_date'], "%b %d, %Y").strftime("%Y-%m-%d")
            })   
        pprint(outputs, indent=8)
    
    # close tab
    driver.close()
    # switch back to shoe listings page
    driver.switch_to.window(driver.window_handles[-1])
    return outputs

def get_all_data_on_page(driver, type):
    time0 = datetime.now()
    within_tolerance = True
    # grab all links to shoes on the page
    
    list_of_shoes = driver.find_elements_by_xpath(
            "//div[@id='srp-river-results']/ul[contains(@class, 'srp-results')]/li"
            )
    print("This page has ", len(list_of_shoes), " shoe listings")
    page_outputs = []
    for i, shoe in enumerate(list_of_shoes):
        title_element = shoe.find_element_by_xpath(".//a[@class='s-item__link']")
        sold_title = title_element.text
        if ebay_validation(sold_title, type)==False:
            continue
        encoded = sold_title.encode("ascii", "ignore")
        sold_title = encoded.decode()
        href_link = title_element.get_attribute("href")

        sold_price = shoe.find_element_by_xpath(".//span[@class='s-item__price']").text
        sold_price = sold_price.replace("$", "")
        sold_date = shoe.find_element_by_xpath(".//div[contains(@class, 's-item__title--tag')]/div/span[contains(@class, 'POSITIVE')]").text
        sold_date = sold_date.replace("Sold ", "")
        
        sold_date_obj = datetime.strptime(sold_date, "%b %d, %Y")
        current_date = datetime.now()
        within_tolerance = (current_date - sold_date_obj) <= timedelta(TOLERANCE)
        if within_tolerance == False:
            break
        
        basic_info = {
            'sold_title': sold_title,
            'sold_price': sold_price,
            'sold_date': sold_date,
            "href_link": href_link
        }
        page_outputs.append(basic_info)
        print("Sneaker Number: ", i)
        print("Trade Title: ", basic_info['sold_title'])
        print("Trade Price: ", basic_info['sold_price'])
        print("Trade Date: ", basic_info['sold_date'])
        print("Trade URL: ", href_link)
        
        
        
    time_used = datetime.now() - time0
    print("Total Time used to collect data on list page in Seconds: ", time_used.total_seconds())
    print("\n\n")
    return within_tolerance, page_outputs

"""
Traverses a list of sneaker names and finds every shoe in that category
saving the dictionary of data scraped from that shoe's page

@param category_list: list of all shoe categories
@param driver: reference to selenium webdriver object
"""
def traverse_sneaker_list(driver, sneaker_lists):
    for i, sneaker in enumerate(sneaker_lists):
        trades = []
        sneaker_name = sneaker['title']
        sneaker_id = sneaker['product_id']
        ebay_search = driver.find_element_by_xpath("//input[contains(@id, 'gh-ac')]")
        ebay_search.clear()
        ebay_search.send_keys(sneaker_name)
        ebay_search.send_keys(Keys.ENTER)
        print("Wait for 5 sec for page reload")
        time.sleep(5)
        print('Page reloaded after search\n\n')
        if i == 0:
            all_filter = driver.find_element_by_xpath("//div[contains(@id, 's0-14-11-0-1-2-6-0-20[8]-4')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", all_filter)
            ActionChains(driver).click(all_filter).perform()
            if not check_for_robot(driver):
                time.sleep(3)
            else: 
                input("hit enter to continue")
            sold_items = driver.find_element_by_xpath("//div[contains(@id, 'c3-subPanel-LH_Sold_Sold%20Items')]/label/div/span")
            auth_guar = driver.find_element_by_xpath("//div[contains(@id, 'c3-subPanel-LH_AV_Authenticity%20Guarantee')]/label/div/span")
            completed_items = driver.find_element_by_xpath("//div[contains(@id, 'c3-subPanel-LH_Complete_Completed%20Items')]/label/div/span")

            ActionChains(driver).click(sold_items).perform()
            ActionChains(driver).click(auth_guar).perform()
            ActionChains(driver).click(completed_items).perform()
            
            apply_button = driver.find_element_by_xpath("//div[contains(@id, 'c3-footerId')]/div[contains(@class, 'x-overlay-footer__apply')]/button")
            ActionChains(driver).click(apply_button).perform()
            print("Start Wait for all filter to applied")
            time.sleep(5)
            print("End Wait for all filter to applied\n\n")     
        input("CLICK 192")

        directory = '../data/ebay/'
        if (not os.path.isdir("../data/ebay/")):
            os.makedirs(directory, exist_ok=True)

        page_url = ""
        page_num = 1
        within_tolerance = True
        while within_tolerance:
            print("Current page: ", page_num)
            if page_url == "":
                res = get_all_data_on_page(driver, sneaker['gender'])
                within_tolerance = res[0]
                trades += res[1]
            else:
                open_link(driver, page_url)
                res = get_all_data_on_page(driver, sneaker['gender'])
                within_tolerance = res[0]
                trades += res[1]

            print("Done for the page\n\n")

            try:
                right_arrows = driver.find_element_by_xpath(
        	    "//a[contains(@class,'pagination__next')]")
            except NoSuchElementException:
                print("Next Page Does not Exist, BREAK here")
                break

            page_url = right_arrows.get_attribute('href')
            loc = page_url.find("_pgn=")
            next_page_num = page_url[loc+5:]
            if '&' in next_page_num:
                arr = next_page_num.split("&")
                next_page_num = arr[0]
            if (page_url == driver.current_url) or int(next_page_num)==page_num:
                # pass
                break
            if(page_num>1):
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
            page_num += 1
        print("Number of Transactions Collected:", len(trades))
        print("Done for the Collect Basic Trade Infos: ", sneaker_name)
        print("Next Step, Dive Deep for Each Trade")
        outputs = []
        for i, trade in enumerate(trades):
            outputs+=get_shoe_trading_data(driver, sneaker_name, trade, sneaker_id)
        ebay_analyzer(outputs, sneaker_id)
        save_dict_to_file(directory, sneaker['ticker_symbol'], outputs)

def save_dict_to_file(directory, ticker, page_dicts):
    with open(directory + ticker + '.csv', 'w') as f:
        w = csv.DictWriter(f, page_dicts[0].keys())
        w.writeheader()
        w.writerows(page_dicts)


def open_link(driver, url):
    global num_opened
    num_opened += 1
    if num_opened % THRESHOLD == 0:
        print("Current Time:", datetime.now())
        print("MEET OPENED LINK THRESHOLD. HIT Enter to Continue")
        input("hit enter to continue")
    while True:
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(.5)

        print("Opening ", url)
        print("num_opened", num_opened, "\t num_opened threshold",num_opened%THRESHOLD)
        driver.get(url)
        if not check_for_robot(driver):
            time.sleep(randint(1,10)) 
            return
        else:
            input("hit enter to restart")
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])


def check_for_robot(driver):
    try:
       driver.find_element_by_xpath("//div[@id='areaTitle']/h1[contains(text(), 'Please verify yourself to continue')]")
       return True
    except NoSuchElementException as e:
        return False

def main():
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')
    action = ActionChains(driver)

    url = 'https://ebay.com/'
    driver.get(url)

    try:
        res = requests.get("http://localhost:8080/api/sneakers/")
        sneakers = res.json()
    except HTTPError as error:
        print(error)
        raise "Failed to get Sneakers Info"
    
    traverse_sneaker_list(driver, sneakers)

    print("All Done!")

   
if __name__ == '__main__':
    main()

