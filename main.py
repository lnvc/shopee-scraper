import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
from dotenv import load_dotenv

load_dotenv('.env')

if not os.path.isdir('images'):
    os.makedirs('images')
driver = webdriver.Chrome()
driver.maximize_window()
driver.get(os.getenv('URL'))
driver.find_element_by_class_name('shopee-popup__close-btn').click()
soup = BeautifulSoup(driver.page_source, 'html.parser')
categories = soup.find_all('a', class_='home-category-list__category-grid')
category_names = [c.get_text() for c in soup.find_all('div', class_='vvKCN3')]
# cat_err_index = []
# if os.path.isfile('i.txt'):
#     with open('i.txt', 'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             cat_err_index.append(int(line.strip()))
            
page_nums = [0,1]
# page_err_index = []
# if os.path.isfile('p.txt'):
#     with open('p.txt', 'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             page_err_index.append(int(line.strip()))

window_before = driver.window_handles[0]
for i in range(0, len(categories)):
# for i in cat_err_index:
    data = {}
    for p in range(0, 2):
    # for p in page_err_index:
        cat_url = str(os.getenv('URL') + categories[i]['href'].replace("'", "%27"))
        driver.execute_script("window.open('{}');".format(str(cat_url + '?page=' + str(p) + '&sortBy=sales')))
        window_after = driver.window_handles[1]
        driver.switch_to.window(window_after)

        time.sleep(1)
        element = driver.find_element_by_class_name('header-with-search__logo-section')
        for k in range(0,7):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.8)

        cat_page = BeautifulSoup(driver.page_source, 'html.parser')
        product_urls = [str(os.getenv('URL') + c.find('a')['href'].replace("'", "%27")) for c in cat_page.find_all('div', class_='col-xs-2-4 shopee-search-item-result__item')]
        # product_err_index = []
        # if os.path.isfile('j.txt'):
        #     with open('j.txt', 'r') as f:
        #         lines = f.readlines()
        #         for line in lines:
        #             product_err_index.append(int(line.strip()))

        if 'link' in data:
            data['link'].extend(product_urls)
        else:
            data['link'] = product_urls
        if categories[i]['href'] == "/Digital-Goods-Vouchers-cat.15580":
            names = [c.get_text().replace("/", " or ").replace('<', '').replace('>', '').replace(':', '').replace('"', '').replace("\\", '').replace('|', '').replace('?', '').replace('*', '') for c in cat_page.find_all('div', class_='_1NoI8_ _16BAGk')]
            prices = [str(php.find_all('span')[0].get_text().replace('₱', '')) + str(php.find_all('span')[1].get_text().replace('₱', '')) for php in cat_page.find_all('div', class_='_1w9jLI _37ge-4 _2ZYSiu')]
            urls = [u.find('img')['src'] for u in  cat_page.find_all('div', class_='_39-Tsj _1tDEiO')]
            if 'product name' in data:
                data['product name'].extend(names)
            else:
                data['product name'] = names
            if 'price' in data:
                data['price'].extend(prices)
            else:
                data['price'] = prices
            data['amount sold'] = [None] * 100
            data['seller'] = [None] * 100
            for k in range(0,50):
                req = requests.get(urls[k])
                if not os.path.isdir('images/' + names[k]):
                    os.makedirs('images/' + names[k])
                with open('images/' + names[k] + '/' + names[k] + '.jpg', 'wb') as f:
                    f.write(req.content)
            df = pd.DataFrame().from_dict(data)
            df.set_index('product name', inplace=True)
            path = str(category_names[i] + '.csv')
            csv = df.to_csv(path, mode='a', header=True)
            print('added all digital goods')
        else:
            for j in range(0, len(product_urls)):
            # for j in product_err_index:
                try: 
                    datum = {}
                    driver.execute_script("window.open('{}');".format(product_urls[j]))
                    driver.switch_to.window(driver.window_handles[2])

                    time.sleep(1.8)
                    details = BeautifulSoup(driver.page_source, 'html.parser')
                    if details.find('button', class_='btn btn-solid-primary btn--m btn--inline shopee-alert-popup__btn'):
                        time.sleep(1.8)
                        driver.find_element_by_css_selector('.btn.btn-solid-primary.btn--m.btn--inline.shopee-alert-popup__btn').click()
                        details = BeautifulSoup(driver.page_source, 'html.parser')
                    name = details.find('div', class_='qaNIZv').find('span').get_text().replace("/", " or ").replace('<', '').replace('>', '').replace(':', '').replace('"', '').replace("\\", '').replace('|', '').replace('?', '').replace('*', '')
                    name = name[:min(121, len(name))]
                    amount = details.find('div', class_='_22sp0A').get_text()
                    seller = details.find('div', class_='_3Lybjn').get_text()
                    price = details.find('div', class_='_3n5NQx').get_text().replace('₱', '')


                    datum['product name'] = [name]
                    datum['amount sold'] = [amount]
                    datum['seller'] = [seller]
                    datum['price'] = [price]
                    datum['link'] = [product_urls[j]]

                    driver.find_elements_by_class_name('product-variation')
                    variation_len = len(driver.find_elements_by_class_name('product-variation'))
                    image_set = set()
                    for ind in range(0, variation_len):
                        time.sleep(1)
                        driver.find_elements_by_class_name('product-variation')[ind].click()
                        time.sleep(1)
                        img_detail = BeautifulSoup(driver.page_source, 'html.parser')
                        if img_detail.find('div', class_='_2JMB9h V1Fpl5'):
                            img = img_detail.find('div', class_='_2JMB9h V1Fpl5')['style'].split('");')[0][23:]
                            if img not in image_set:
                                image_set.add(img)
                                req = requests.get(img)
                                if not os.path.isdir('images/' + name):
                                    os.makedirs('images/' + name)
                                with open('images/' + name + '/' + name + '(' + str(ind) + ').jpg', 'wb') as f:
                                    f.write(req.content)
                                    print('download image: ', img)

                    driver.find_elements_by_class_name('_2MDwq_')[0].click()
                    time.sleep(0.8)
                    image_len = len(driver.find_elements_by_css_selector('.ZPN9uD._2e-ot7'))
                    for ind in range(0, image_len):
                        driver.find_elements_by_css_selector('.ZPN9uD._2e-ot7')[ind].click()
                        img_detail = BeautifulSoup(driver.page_source, 'html.parser')
                        if img_detail.find('div', class_='_3TtC8T V1Fpl5'):
                            img = img_detail.find('div', class_='_3TtC8T V1Fpl5')['style'].split('");')[0][23:]
                            if img not in image_set:
                                image_set.add(img)
                                req = requests.get(img)
                                if not os.path.isdir('images/' + name):
                                    os.makedirs('images/' + name)
                                with open('images/' + name + '/' + name + '(' + str(ind + variation_len + 1) + ').jpg', 'wb') as f:
                                    f.write(req.content)
                                    print('downloaded image: ', img)
                    
                    df = pd.DataFrame().from_dict(datum)
                    df.set_index('product name', inplace=True)
                    path = str(category_names[i] + '.csv')
                    if j == 0:
                        df.to_csv(path, mode='a', header=True)
                    else:
                        df.to_csv(path, mode='a', header=False)
                except:
                    print('timeout error. failed to add product with category index ' + str(i) + ', page index ' + str(p) +', and product index ' + str(j))
                    with open('i.txt', 'a') as f:
                        f.write(str(i) + '\n')
                    with open('p.txt', 'a') as f:
                        f.write(str(p) + '\n')
                    with open('j.txt', 'a') as f:
                        f.write(str(j) + '\n')
                driver.close()
                driver.switch_to.window(driver.window_handles[1])
        
        driver.close()
        driver.switch_to.window(window_before)

