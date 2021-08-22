from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import telegram_send
from datetime import date
import schedule
import os

searchUrlPrefix = 'https://aliexpress.ru/wholesale?SortType=total_tranpro_desc&maxPrice=200&SearchText='
categoriesTitles = ['Серьги женские', 'Подвески женские', 'Браслет женский']
bestProductSalesCount = 7000
maxProductsResponseCount = 10


def job():
    options = Options()

    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')

    driver = webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')), chrome_options=options)

    # driver = webdriver.Chrome('/usr/local/bin/chromedriver')

    telegram_send.send(messages=["Новая выборка за *" + date.today().strftime("%d %B, %Y") + "*"],
                       parse_mode='markdown')

    for title in categoriesTitles:
        bot_message = ''
        best_products_urls = []
        current_category = title
        driver.get(searchUrlPrefix + current_category)
        time.sleep(5)
        print(driver.title)
        print(driver.current_url)
        close_element = driver.find_elements_by_class_name("next-dialog-close")
        if len(close_element) > 0:
            close_element[0].click()
            time.sleep(1)

        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        time.sleep(1)

        product_cards = driver.find_elements_by_class_name("product-card")
        print('Elements count on page: ' + str(len(product_cards)))

        for product in product_cards:
            url = product.find_element_by_class_name("item-title").get_attribute('href')
            sale_elements = product.find_elements_by_class_name("sale-value-link")
            if len(sale_elements) > 0:
                sale_element = sale_elements[0]
                sales_value = sale_element and sale_element.text.split(" ")[0] or ''
                orders_count = sales_value and int(sales_value) or 0
                if orders_count >= bestProductSalesCount:
                    best_products_urls.append(url)

        bot_message += 'Категория *' + current_category + '*\n'
        bot_message += 'Топ *' + str(maxProductsResponseCount) + '*\n'
        bot_message += '👇\n'
        telegram_send.send(messages=[bot_message], parse_mode='markdown')
        for count in range(maxProductsResponseCount):
            telegram_send.send(messages=[best_products_urls[count]])

    driver.close()


job()
schedule.every(7).days.at("10:00").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)
