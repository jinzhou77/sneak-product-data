import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

import time
import numpy as np
from datetime import datetime, timedelta
from pprint import pprint

import csv
from random import randint

import requests

sneakData_backend = "http://localhost:8080/api/sneakers/"
skip_page = "https://stockx.com/nike/sb?page=2"
first_category = True # skips to start on a specified page if set to true

BREAKS = False # if true, gets data for one sneaker per page

# after opening a link, wait this long
PAGE_WAIT = 30

# number of links before long wait
THRESHOLD = 50

# after opening THRESHOLD number of links wait this long
THRESHOLD_WAIT = 3600

# after encountering the "Are you a robot?" page wait this long
ROBOT_PAGE_WAIT = 3600

num_opened = 0

TOLERANCE = 1

CURRENT_DATE = datetime.now()

def get_shoe_trading_data(url, driver, directory,page_wait=PAGE_WAIT):
    
    output = {}
    outputs = []
    # open link to shoe
    open_link(driver,url,page_wait=page_wait)

    try:
        # save name of sneaker
        name =  driver.find_element_by_xpath("//div[@class='col-md-12']/h1").text

        # save ticker code
        ticker = driver.find_element_by_css_selector('.soft-black').text
    except:
        print('get name and ticker faield')

    try:
        last_sale_block = driver.find_element_by_xpath("//div[contains(@class, 'last-sale-block')]")
        view_all_sales = last_sale_block.find_element_by_xpath("//button[contains(text(), 'View All Sales')]")
        action = ActionChains(driver)
        action.click(view_all_sales).perform()
        time.sleep(5)
    except:
        print("failed to open sales history")
    
    try:
        index = 1
        while True:
            e = driver.find_element_by_xpath("//button[contains(text(), 'Load More')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", e)
            print("Click %d start" % index)
            ActionChains(driver).move_to_element(WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More')]")))).click().perform()
            print("Click %d Done, sleep for 3s" % index)
            index+=1
            time.sleep(3)

    except NoSuchElementException:
        print("Not able to find the Load More Button, sleep for 10s")
        time.sleep(10)

    try:
        table = driver.find_element_by_xpath("//table[contains(@class, 'activity-table')]")
        trade_infos = []
        for row in table.find_elements_by_xpath(".//tr"):
            trade_info = [td.text for td in row.find_elements_by_tag_name("td")] #[]
            if len(trade_info) > 0:
                trade_infos.append(trade_info) #[[],[],[],[],[]]
        for i, trade_info in enumerate(trade_infos):
            date_obj = datetime.strptime(trade_infos[i][0], "%A, %B %d, %Y")
            within_tolerance = (CURRENT_DATE - date_obj) <= timedelta(days=TOLERANCE)
            if within_tolerance == False:
                break

            outputs.append({
                'name': name,
                'ticker': ticker,
                'date': trade_infos[i][0],
                'time': trade_infos[i][1],
                'size': trade_infos[i][2],
                'price': trade_infos[i][3],
            })
    except NoSuchElementException:
        print("Historical Data is not available")
        trade_date = {'date': 'N/A'}
        output.update(trade_date)
        trade_time = {'time': 'N/A'}
        output.update(trade_time)
        trade_size = {'size': 'N/A'}
        output.update(trade_size)
        trade_price = {'price': 'N/A'}
        output.update(trade_price)
        outputs.append(output)
    
    save_shoe_trade_info_to_file(directory, ticker, outputs)
    # close tab
    driver.close()
    # switch back to shoe listings page
    driver.switch_to.window(driver.window_handles[-1])

    return outputs

def save_shoe_trade_info_to_file(directory, ticker, shoe_dicts):
    with open(directory  + str(ticker) + ".csv", 'w') as f:
        w = csv.DictWriter(f, shoe_dicts[0].keys())
        w.writeheader()
        w.writerows(shoe_dicts)


def open_link(driver, url, page_wait=PAGE_WAIT):

    # set local num_opened to reference of global num_opened
    global num_opened
    num_opened += 1
    if num_opened % THRESHOLD == 0:
        threshold_wait = randint(600, 3600)
        print("MEET OPENED LINK THRESHOLD. Sleeping for ", threshold_wait,  "seconds...")
        print("Current Time:", datetime.now())
        time.sleep(threshold_wait)

    while True:
        # open new tab
        driver.execute_script("window.open();")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(.5)

        # open link
        print("Opening ", url)
        print("num_opened", num_opened, "\t num_opened%THRESHOLD",num_opened%THRESHOLD)
        driver.get(url)
        # check page for robot deterrent
        if not check_for_robot(driver):
            # return if it's not the robot page
            new_link_wait = randint(1,10)
            print("Open New Link, Wait for ", new_link_wait, " seconds")
            time.sleep(new_link_wait) # wait for a little bit so as to not make too many requests
            return
        else:
            input("hit enter to restart")
            # close tab
            driver.close()
            # switch back to previous page
            driver.switch_to.window(driver.window_handles[-1])

def check_for_robot(driver):
    try:
        print(driver.find_element_by_xpath('//h1').text.lower().strip())
        if driver.find_element_by_xpath('//h1').text.lower().strip() == "Please verify you are a human".lower().strip():
            return True
        else:
            return False
    except NoSuchElementException as e:
        return False

def get_all_sneaker_link():
    links = []
    res = requests.get(url=sneakData_backend)
    for r in res.json():
        links.append(r['url'])
    return links

def main():
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')
    driver.maximize_window()

    url = 'https://stockx.com/'
    driver.get(url)
    print("Sign In to your StockX Account")
    print("Username: jinzhou66@yahoo.com")
    print("Password: jJ8254164!")
    input("hit enter after login")
    trading_directory = "../data/stockX/trade/"
    if (not os.path.isdir("../data/stockX/trade/")):
        # create the desired directory
        os.makedirs(trading_directory, exist_ok=True)
    links = get_all_sneaker_link()
    for index, link in enumerate(links):
        print("Sneaker:", index)
        output = get_shoe_trading_data(link, driver, trading_directory)
        pprint(output)
    print("All Done")


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
