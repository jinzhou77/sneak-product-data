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

from pprint import pprint

import csv

from random import randint

import requests
from datetime import datetime, timedelta

skip_page = "https://stockx.com/retro-jordans/air-jordan-1/release-date?page=16"
first_category = False # skips to start on a specified page if set to true

# after opening a link, wait this long
PAGE_WAIT = 20

# number of links before long wait
THRESHOLD = 55

num_opened = 0

CURRENT_DATE = datetime.now() - timedelta(1)

TOLERANCE = 1

NUMBER_OF_SNEAKERS = 10

def get_shoe_data(url, driver, directory, sneaker_basic, trading_directory, complex_image_path=True):
    output = {}
    open_link(driver,url)

    output.update({'url' : url})

    try:
        name = {'name' : sneaker_basic['title']}
        output.update(name)
        
        sales_last_72 = {'sales_last_72': sneaker_basic['sales_last_72']}
        output.update(sales_last_72)

        ticker_code = driver.find_element_by_css_selector('.soft-black').text
        ticker = {'ticker' : ticker_code}
        output.update(ticker)

        if complex_image_path:
            image_path = directory[:7] + "/images" + directory[7:]
        else:
            image_path = directory

        if (not os.path.isdir(image_path)):
            os.makedirs(image_path, exist_ok=True)

        image_path = image_path + ticker['ticker'] + ".jpg"

        if complex_image_path:
            output.update({'image_path' : image_path[7:]}) 
        else:
            output.update({'image_path' : image_path})

        r = requests.get(
            	driver.find_element_by_xpath("//img[@data-testid='product-detail-image']").get_attribute('src'))
        with open(image_path, 'wb') as f:
            f.write(r.content) 
    except:
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        return {}

    try:
        release_date = {
            'release_date'  : driver.find_element_by_xpath(
                                  "//span[@data-testid='product-detail-release date']").text
            }
    except:
        release_date = {'release_date'	: 'N/A'}
    output.update(release_date)
    
    try:
        retail_price = {
            'retail_price'  : driver.find_element_by_xpath(
                                  "//span[@data-testid='product-detail-retail price']").text
            }
    except:
        retail_price = {'retail_price' : 'N/A'}
    output.update(retail_price)

    try:
        style_code = {'style_code' : driver.find_element_by_xpath("//span[@data-testid='product-detail-style']").text}
    except:
        style_code = {'style_code' : 'N/A'}
    output.update(style_code)

    try:
        colorway = {'colorway' : driver.find_element_by_xpath("//span[@data-testid='product-detail-colorway']").text}
    except:
        colorway = {'colorway' : 'N/A'}
    output.update(colorway)

    # Code that does not need for now 
    gauges_wrapper = driver.find_element_by_xpath("//div[contains(@class, 'gauges-wrapper')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", gauges_wrapper)
    gauges = driver.find_elements_by_xpath("//div[@class='gauges']/div[@class='gauge-container']")

    # old code; not sure why I did it this way but it still works so I'm gonna leave it
    for gauge in gauges:
        gauge_text = gauge.find_element_by_css_selector("div:nth-child(2)").text.lower()
        print(gauge_text)
        if gauge_text == "# of sales":
            # get # of sales
            number_of_sales = gauge.find_element_by_css_selector("div:nth-child(3)").text
            if number_of_sales != "--":
                output.update({'number_of_sales' : number_of_sales})
            else:
                output.update({'number_of_sales' : "0"})

        elif "price premium" in gauge_text:
            # get price premium
            price_premium = gauge.find_element_by_css_selector("div:nth-child(3)").text
            if price_premium != "--":
                output.update({'price_premium' : price_premium})
            else:
                output.update({'price_premium' : "N/A"})

        elif gauge_text == "average sale price":
            # get average sale price
            average_sale_price = gauge.find_element_by_css_selector("div:nth-child(3)").text
            if average_sale_price != "--":
                output.update({'average_sale_price' : average_sale_price})
            else:
                output.update({'average_sale_price' : "0.0"})

    # get_shoe_trading_data(ticker_code, sneaker_basic['title'], driver, trading_directory)
    
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])

    return output


def get_shoe_trading_data(ticker, sneaker_title, driver, directory):
    
    output = {}
    outputs = []

    try:
        last_sale_block = driver.find_element_by_xpath("//div[contains(@class, 'last-sale-block')]")
        view_all_sales = last_sale_block.find_element_by_xpath("//button[contains(text(), 'View All Sales')]")
        action = ActionChains(driver)
        action.click(view_all_sales).perform()
        time.sleep(10)
    except:
        print("failed to open sales history")
    
    try:
        index = 1
        while True: #Fucking stockX sometimes does not sort the trading data, have to expand all trade data here. Fucking dumb ass shit
            e = driver.find_element_by_xpath("//button[contains(text(), 'Load More')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", e)
            print("Click %d start" % index)
            ActionChains(driver).move_to_element(WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More')]")))).click().perform()
            print("Click %d Done" % index)
            time.sleep(2)
            index+=1
    except NoSuchElementException:
        print("Not able to find the Load More Button, sleep for 10s")

    try:
        table = driver.find_element_by_xpath("//table[contains(@class, 'activity-table')]")
        trade_infos = []
        for row in table.find_elements_by_xpath(".//tr"):
            trade_info = [td.text for td in row.find_elements_by_tag_name("td")] #[]
            if len(trade_info) > 0:
                trade_infos.append(trade_info) #[[],[],[],[],[]]
        for i, trade_info in enumerate(trade_infos):
            date_obj = datetime.strptime( trade_infos[i][0], "%A, %B %d, %Y")
            within_tolerance = (CURRENT_DATE - date_obj) <= timedelta(TOLERANCE)
            if within_tolerance == True:
                outputs.append({
                    'name': sneaker_title,
                    'ticker': ticker,
                    'date': trade_infos[i][0],
                    'time': trade_infos[i][1],
                    'size': trade_infos[i][2],
                    'price': trade_infos[i][3],
                })
    except NoSuchElementException:
        print("Historical Data is not available")
        name = {'name': sneaker_title}
        output.update(name)
        ticker = {'ticker': ticker}
        output.update(ticker)
        trade_date = {'date': 'N/A'}
        output.update(trade_date)
        trade_time = {'time': 'N/A'}
        output.update(trade_time)
        trade_size = {'size': 'N/A'}
        output.update(trade_size)
        trade_price = {'price': 'N/A'}
        output.update(trade_price)
        outputs.append(output)
    
    pprint(outputs, indent=12)

    save_shoe_trade_info_to_file(directory, ticker, outputs)

def get_all_data_on_page(driver, directory, trading_directory, number_of_shoes):
    page_dicts = []
    list_of_shoes = driver.find_elements_by_xpath(
            "//div[@class='browse-grid']/div[contains(@class,'tile browse-tile')]"
            )
    print("This page has ", len(list_of_shoes), " shoe listings")
    
    if len(list_of_shoes) > number_of_shoes:
        index = 0
        while number_of_shoes > 0:
            shoe_link_elem = list_of_shoes[index].find_element_by_xpath(".//a")
            shoe_link = shoe_link_elem.get_attribute('href')
            shoe_title = list_of_shoes[index].find_element_by_xpath(".//div[contains(@class, 'css-pgwwog-PrimaryText')]").text
            shoe_72_sales = list_of_shoes[index].find_element_by_xpath(".//div[contains(@class, 'most-active')]").text
            validation_res = sneaker_validation(shoe_title, shoe_72_sales)
            if validation_res[0] == False:
                index+=1
                continue
            shoe_dict = get_shoe_data(shoe_link, driver, directory, validation_res[1], trading_directory)
            pprint(shoe_dict, indent=8)      
            page_dicts.append(shoe_dict)
            index+=1
            number_of_shoes-=1
    else:
        for i, shoe in enumerate(list_of_shoes):
            shoe_link_elem = shoe.find_element_by_xpath(".//a")
            shoe_link = shoe_link_elem.get_attribute('href')
            shoe_title = shoe.find_element_by_xpath(".//div[contains(@class, 'css-pgwwog-PrimaryText')]").text
            shoe_72_sales = shoe.find_element_by_xpath(".//div[contains(@class, 'most-active')]").text
            validation_res = sneaker_validation(shoe_title, shoe_72_sales)
            if validation_res[0] == False:
                continue
            shoe_dict = get_shoe_data(shoe_link, driver, directory, validation_res[1], trading_directory)
            pprint(shoe_dict, indent=8)
            page_dicts.append(shoe_dict)
        
    return page_dicts

def sneaker_validation(title, shoe_72_sales):
    if 'N/A' in shoe_72_sales or 'N/A' in title:
        print("N/A value found in sneaker title or release_date.")
        return (False, None)

    # #validation on release_date
    # date_str = release_date.replace("Release: ", "")
    # print("Shoe Release Date:", date_str)
    # datetime_obj = datetime.strptime(date_str, "%m/%d/%Y")
    # current_date = datetime.now()
    # if datetime_obj > current_date:
    #     print("The Sneaker is not released yet")
    #     return (False, None)

    # validation on number of sale over past 72 hours
    # sales_str = shoe_72_sales.replace(" # Of Sales: ", "")
    print("Number of shoes sold in past 72 hours", shoe_72_sales.replace("# Of Sales: ", ""))
    try:
        sales_int = int(shoe_72_sales.replace("# Of Sales: ", ""))
    except:
        return (False, None)
    
    #validation on sneaker name
    invalid_names = ['infant', 'kids', '(gs)', '(ps)', '(i)', '(td)']
    print("Shoe Title:", title)
    sneaker_name = title.lower()
    for elem in invalid_names:
        if elem in sneaker_name:
            return (False, None)

    basic_info = {
        'sales_last_72': sales_int,
        'title': title
    }
    return (True, basic_info)

def get_category_data(link_to_shoe_category, driver):
    global first_category

    category_directory = link_to_shoe_category[19:]

    category_directory = "../data/sneakers/" + category_directory.replace("-", "") + "/"
    # if the desired directory doesn't exist
    if (not os.path.isdir("../data/sneakers/" + category_directory.replace("-", ""))):
        # create the desired directory
        os.makedirs(category_directory.replace("-", ""), exist_ok=True)

    trading_directory = link_to_shoe_category[19:]
    trading_directory = "../data/stockX/sneakers/" + trading_directory + "/"
    # if the desired directory doesn't exist
    if (not os.path.isdir("../data/stockX/sneakers/" + trading_directory)):
        # create the desired directory
        os.makedirs(trading_directory, exist_ok=True)

    if first_category:
        print("First pass detected skipping to", skip_page)
        link_to_shoe_category = skip_page
        first_category = False

    # go to next page if there is another page

    loc = link_to_shoe_category.find('?page=')
    if loc != -1:
        page_num = int(link_to_shoe_category[loc+6:])
    else:
        page_num = 1

    page_url = link_to_shoe_category
    # get all data on the page, if there is a next page get the info on that page too
    release_date_toggle = False
    number_of_shoes = NUMBER_OF_SNEAKERS
    shoes = []
    while number_of_shoes > 0:
        # open link to category in new tab
        open_link(driver,page_url)
        if release_date_toggle == False:
            input("Hit Enter after Sort the sneakers with most popular")
            release_date_toggle = True
        page_data = get_all_data_on_page(driver, category_directory, trading_directory, number_of_shoes)
        number_of_shoes-=len(page_data)
        shoes+=page_data
        # check if the right arrow refers to stockx home page because for some 
        # reason that's what the right arrow does if there isn't a next page
        try:
            right_arrows = driver.find_elements_by_xpath(
        	"//ul[contains(@class,'ButtonList')]/a[contains(@class,'css-n29mp3-NavigationButton')]")

            page_url = right_arrows[1].get_attribute('href')
            if (page_url == 'https://stockx.com/'):
                # pass
                break
        except:
            print("Next Page Does Not Exist")
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            break

        # before going to next page, close the current page
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])

        page_num += 1
    save_dict_to_file(category_directory, shoes)

def traverse_model_category_list(brand_category_list, brand_name, driver):
    model_links = []
    for brand_category in brand_category_list:
        shoe_models = brand_category.find_elements_by_xpath("./li/a")
        if brand_name.lower() == "air jordan":
            wanted_models = ['1','3','4','5','6','7','9','11','12','13', 'jordan off-white']
        elif brand_name.lower() == 'adidas':
            wanted_models = ['yeezy', 'nmd', 'ultra boost']
        elif brand_name.lower() =='nike':
            wanted_models = ['kd', 'kobe', 'lebron', 'air force', 'air max', 'basketball']
            
        for models in shoe_models:
            if(models.text.lower() in wanted_models):
                model_links.append(models.get_attribute('href'))
    print("Number of shoe models:", len(model_links))
    for link in model_links:
        get_category_data(link, driver)

        # #close category page
        # driver.close()
        # driver.switch_to.window(driver.window_handles[0])


def save_dict_to_file(directory, page_dicts):
    with open(directory + "result.csv", 'w') as f:
        w = csv.DictWriter(f, page_dicts[0].keys())
        w.writeheader()
        w.writerows(page_dicts)


def save_shoe_trade_info_to_file(directory, ticker, shoe_dicts):
    with open(directory  + str(ticker) + ".csv", 'w') as f:
        w = csv.DictWriter(f, shoe_dicts[0].keys())
        w.writeheader()
        w.writerows(shoe_dicts)

def get_brands(driver):

    browse_sneakers_dropdown(driver)
    brand_list_dropdown = driver.find_element_by_xpath("//ul[contains(@class, 'category-level-2')]")
    brand_list_dropdown = brand_list_dropdown.find_elements_by_xpath('./li/a')

    # delete upcoming releases page
    del brand_list_dropdown[-1]

    return brand_list_dropdown

def browse_sneakers_dropdown(driver):
    action = ActionChains(driver)

    wait = WebDriverWait(driver, 10)
    # hover over  browse menu
    browse_dropdown = driver.find_element_by_xpath("//li[@class='dropdown browse-dropdown']") 
    action.move_to_element(browse_dropdown).perform()

    # hover over sneakers menu
    sneaker_dropdown = driver.find_element_by_xpath("//a[contains(@data-testid,'submenu-sneakers')]")
    action.move_to_element(sneaker_dropdown).perform()

def open_link(driver, url):

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
            #print("Detected robot page, waiting ", ROBOT_PAGE_WAIT, "seconds...")
            #time.sleep(ROBOT_PAGE_WAIT)

            input("hit enter to restart")
            # close tab
            driver.close()
            # switch back to previous page
            driver.switch_to.window(driver.window_handles[-1])
        
def check_for_robot(driver):
    try:
        if driver.find_element_by_xpath('//h1').text.lower().strip() == "Please verify you are a human".lower().strip():
            return True
        else:
            return False
    except NoSuchElementException as e:
        return False


def main():
    
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    
    # firefox_profile = webdriver.FirefoxProfile()
    # firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
    # driver = webdriver.Firefox(firefox_profile=firefox_profile)
    
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')
    
    # driver = webdriver.Edge('./msedgedriver.exe')
    
    driver.maximize_window()


    action = ActionChains(driver)
    
    url = 'https://stockx.com/'
    driver.get(url)
    print("Sign In to your StockX Account")
    print("Username: jinzhou66@yahoo.com")
    print("Password: jJ8254164!")

    input("hit enter after login")

    print("done waiting\n\n")

    brands = get_brands(driver)
    
    for brand_element in brands:
        browse_sneakers_dropdown(driver)
        print(brand_element.text)
        action.move_to_element(brand_element).perform()
        print("hovering on ",brand_element.text)
        time.sleep(1)
        brand_categories = driver.find_elements_by_xpath("//ul[contains(@class, 'category-level-3')]")

        # cleans out fake/empty links that wouldn't be accessible to normal users
        brand_categories = [x for x in brand_categories if x.text.strip() != '']

        traverse_model_category_list(brand_categories, brand_element.text, driver)

        print("All Done!")

out = None
if __name__ == '__main__':
    out = main()