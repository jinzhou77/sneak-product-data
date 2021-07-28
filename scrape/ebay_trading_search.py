import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import time
import numpy as np
from datetime import datetime, timedelta
from pprint import pprint

import csv

import requests

first_category = True # skips to start on a specified page if set to true

BREAKS = False # if true, gets data for one sneaker per page

# after opening a link, wait this long
PAGE_WAIT = 5

# number of links before long wait
THRESHOLD = 60

# after opening THRESHOLD number of links wait this long
THRESHOLD_WAIT = 1200

# after encountering the "Are you a robot?" page wait this long
ROBOT_PAGE_WAIT = 18000

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

def get_shoe_trading_data(driver, sneaker_name, info_dict, page_wait=PAGE_WAIT):
    outputs = []
    
    #test
    # open_link(driver, "https://www.ebay.com/itm/393460485447?epid=2310847576&hash=item5b9c128d47:g:gW0AAOSwcrRg-o~C", page_wait=page_wait)

    open_link(driver,info_dict['href_link'],page_wait=page_wait)

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
            open_link(driver,purchaseHistURL,page_wait=page_wait)
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
                        'name': sneaker_name,
                        'title': info_dict['sold_title'],
                        'seller': seller,
                        'trade_url': info_dict['href_link'],
                        'condition': condition,
                        'ship_fee': ship_fee,
                        'size': rows[i][1],
                        'sold_price':  rows[i][2].replace("US $", ""),
                        'sold_date': date_str
                    })
                else:
                    sold_date_arr =  rows[i][3].split("at")
                    date_obj = datetime.strptime(sold_date_arr[0], "%d %b %Y ")
                    date_str = datetime.strftime(date_obj, "%b %d, %Y")
                    outputs.append({
                        'name': sneaker_name,
                        'title': info_dict['sold_title'],
                        'seller': seller,
                        'trade_url': info_dict['href_link'],
                        'condition': condition,
                        'ship_fee': ship_fee,
                        'size': shoe_size,
                        'sold_price':  rows[i][1].replace("US $", ""),
                        'sold_date': date_str
                    })
        except NoSuchElementException:
            print("Purchase List does not exist, find the data in this page")
            shoe_size = driver.find_element_by_xpath("//td[contains(text(), 'US Shoe Size')]/following-sibling::td").text
            outputs.append({
                'name': sneaker_name,
                'title': info_dict['sold_title'],
                'seller': seller,
                'trade_url': info_dict['href_link'],
                'condition': condition,
                'ship_fee': ship_fee,
                'size': shoe_size,
                'sold_price':  info_dict['sold_price'],
                'sold_date': info_dict['sold_date']
            })   
        pprint(outputs, indent=8)
    
    # close tab
    driver.close()
    # switch back to shoe listings page
    driver.switch_to.window(driver.window_handles[-1])
    return outputs

"""
helper function that gets all shoe data on the current open page and returns it in a list of dictionaries

@param driver: reference to selenium webdriver object
@param directory: passed to get_shoe_data for organized image storage
@return: list of the gathered data from all shoes on a page
"""
def get_all_data_on_page(driver):
    time0 = datetime.now()
    within_tolerance = True
    # grab all links to shoes on the page
    print("Click 192 Now!!!!")
    time.sleep(15)
    list_of_shoes = driver.find_elements_by_xpath(
            "//div[@id='srp-river-results']/ul[contains(@class, 'srp-results')]/li"
            )


    print("This page has ", len(list_of_shoes), " shoe listings")
    page_outputs = []
    for i, shoe in enumerate(list_of_shoes):
        title_element = shoe.find_element_by_xpath(".//a[@class='s-item__link']")
        sold_title = title_element.text
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
        if BREAKS:
            break
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
        sneaker_name = sneaker
        sneaker = sneaker.replace("adidas", '')
        if('Yeezy Boost 350 V2 Black Red (2017/2020)' in sneaker):
            sneaker = "Yeezy Boost 350 V2 Black Red"
        ebay_search = driver.find_element_by_xpath("//input[contains(@id, 'gh-ac')]")
        ebay_search.clear()
        ebay_search.send_keys(sneaker)

        ebay_search.send_keys(Keys.ENTER)
        print("Wait for 5 sec for page reload")
        time.sleep(5)
        print('Page reloaded after search\n\n')
        if i == 0:
            all_filter = driver.find_element_by_xpath("//div[contains(@id, 's0-14-11-0-1-2-6-0-20[8]-4')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", all_filter)
            ActionChains(driver).click(all_filter).perform()
            time.sleep(3)

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

        directory = '../data/ebay/sneakers/' + sneaker.replace(" ", "") + '/'
        if (not os.path.isdir("../data/ebay/sneakers/" + sneaker.replace(" ", "") + '/')):
            os.makedirs(directory, exist_ok=True)

        #skip to page 
        # page_url = "https://www.ebay.com/sch/i.html?_fsrp=1&rt=nc&_from=R40&_nkw=Yeezy+Boost+350+V2+Black+Red&_sacat=0&LH_Sold=1&LH_AV=1&LH_Complete=1&_pgn=2"
        
        page_url = ""
        page_num = 1
        within_tolerance = True
        while within_tolerance:
            print("Current page: ", page_num)
            if page_url == "":
                res = get_all_data_on_page(driver)
                within_tolerance = res[0]
                trades += res[1]
            else:
                open_link(driver, page_url,page_wait=PAGE_WAIT)
                res = get_all_data_on_page(driver)
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
            if (page_url == driver.current_url) or int(next_page_num)==page_num or BREAKS:
                # pass
                break
            if(page_num>1):
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
            page_num += 1
        print("Done for the Collect Basic Trade Infos: ", sneaker_name)
        print("Next Step, Dive Deep for Each Trade")
        outputs = []
        for i, trade in enumerate(trades):
            outputs+=get_shoe_trading_data(driver, sneaker_name, trade)
        save_dict_to_file(directory, outputs)

        
"""
helper function to save lists of dictionaries to the correct file

@param directory: directory to be saved in
@param page_num: number of the page it was pulled from
@param page_dicts: list of data-containing dictionaries
"""
def save_dict_to_file(directory, page_dicts):
    with open(directory + "results.csv", 'w') as f:
        w = csv.DictWriter(f, page_dicts[0].keys())
        w.writeheader()
        w.writerows(page_dicts)


"""
open_link

Opens a link in a new tab
Before returning, check to see if that page is the "are you a robot?" page
If it is, wait 30 minutes and try again, repeat until you get a different page

@param driver: reference to selenium webdriver object
@param url: url of the new tab that you're trying to open
"""
def open_link(driver, url, page_wait=PAGE_WAIT):

    # set local num_opened to reference of global num_opened
    global num_opened
    num_opened += 1
    if num_opened % THRESHOLD == 0:
        print("MEET OPENED LINK THRESHOLD. Sleeping for ", THRESHOLD_WAIT,  "seconds...")
        print("Current Time:", datetime.now())
        time.sleep(THRESHOLD_WAIT)

    while True:
        # open new tab
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(.5)

        # open link
        print("Opening ", url)
        print("num_opened", num_opened, "\t num_opened threshold",num_opened%THRESHOLD)
        driver.get(url)
        # check page for robot deterrent
        if not check_for_robot(driver):
            # return if it's not the robot page
            time.sleep(page_wait) # wait for a little bit so as to not make too many requests
            return
        else:
            #print("Detected robot page, waiting ", ROBOT_PAGE_WAIT, "seconds...")
            #time.sleep(ROBOT_PAGE_WAIT)

            input("hit enter to restart")
            # close tab
            driver.close()
            # switch back to previous page
            driver.switch_to.window(driver.window_handles[-1])

def get_sneaker_names():
    res = requests.get("http://localhost:8080/api/sneakers/")
    data = res.json()
    sneakers = []
    for sneaker in data:
        sneakers.append(sneaker.get('style_name'))
    return sneakers

"""
check_for_robot

returns True if the current open page is the "are you a robot?" page
else return false

@param driver: reference to selenium webdriver object
"""
def check_for_robot(driver):
    try:
       driver.find_element_by_xpath("//div[@id='areaTitle']/h1[contains(text(), 'Please verify yourself to continue')]")
       return True
    except NoSuchElementException as e:
        return False


"""
Main function
Calls get_brands to obtain elements
"""
def main():
    #profile = webdriver.FirefoxProfile()
    #profile.set_preference("general.useragent.override"
    #    , "Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0")
    #profile.set_preference("javascript.enabled", True)
    driver = webdriver.Firefox()
    action = ActionChains(driver)

    # url = 'https://stockx.com/adidas-yeezy-boost-350-v2-lundmark-reflective'
    # driver.get(url)
    url = 'https://ebay.com/'
    driver.get(url)
    print("done waiting\n\n")

    sneaker_names = get_sneaker_names()
    
    traverse_sneaker_list(driver, sneaker_names)

    print("All Done!")

out = None
if __name__ == '__main__':
    out = main()

#driver = webdriver.Firefox()
#driver.get("https://stockx.com")
#brands = get_brands(driver)
##driver.execute_script("window.open('');")
##driver.switch_to.window(driver.window_handles[-1])
##driver.get("https://stockx.com/adidas/yeezy?page=6")
#pprint(get_category_data(brands[0], driver))
