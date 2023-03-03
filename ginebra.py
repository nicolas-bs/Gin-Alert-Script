"""
This email script alert aims to verify discount gins within three different Retail Stores in Colombia: Jumbo, Merquo, Carulla
"""
#! /usr/bin/python3

# Basic Libraries
import pandas as pd
import random   
import requests, re
import sys, os
import time


# Selenium Library
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

# Email Library
from pretty_html_table import build_table
from dotenv import load_dotenv
load_dotenv()

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib, ssl


def get_driver():
    option = webdriver.ChromeOptions()
    option.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    option.add_argument('--start-maximized')
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--headless=new")
    driverService = Service('/Users/nicolasbenavides/Downloads/chromedriver')
    driver = webdriver.Chrome(service=driverService, options=option)
    print('Instance Created')
    return driver

# Jumbo
def jumbo_extract(driver):
    driver.get('https://www.tiendasjumbo.co')
    wait = WebDriverWait(driver, 40)
    action = ActionChains(driver)
    action.click(on_element  = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'tiendasjumboqaio-jumbo-custom-pages-2-x-sliderRightArrow')))).perform()

    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Vinos y licores"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Ginebras"]'))).click()
    
    time.sleep(random.uniform(2.0, 3.5))
    
    main_list = []
    main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtex-product-summary-2-x-container")))
    
    def extract_mainbox(main_box):
        for detail in main_box:
            nombre = detail.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-productBrand').text
            try:
                precio = detail.find_elements(By.CLASS_NAME, 'tiendasjumboqaio-jumbo-minicart-2-x-price')[1].text
            except:
                precio = detail.find_element(By.CLASS_NAME, 'tiendasjumboqaio-jumbo-minicart-2-x-price').text
            try:
                descuento = detail.find_element(By.CLASS_NAME, "tiendasjumboqaio-jumbo-minicart-2-x-containerPercentageFlag").text
            except:
                descuento = float('nan')
            main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Jumbo'})
            time.sleep(random.uniform(1.0, 1.5))
    
    extract_mainbox(main_box)

    try:
        click_button = wait.until(EC.visibility_of_element_located((By.XPATH ,'//button[text()="2"]')))
    
        if click_button.is_displayed():
            click_button.click()
            extract_mainbox(main_box)
    except:
        pass

    df = pd.DataFrame(main_list)
    df['Descuento'].apply(lambda x: str(x).replace(' ', '') if not pd.isna(x) else float('nan'))
    print(f'{len(df)} {df.Store[0]} items was extracted')
    driver.quit()
    return df

# Olimpica
def olimpica_extract(driver):
    driver.get('https://www.olimpica.com/')
    wait = WebDriverWait(driver, 30)
    action = ActionChains(driver)

    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Departamento"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "BOGO")]'))).click()
    
    time.sleep(random.uniform(2.0, 3.5))
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Ciudad"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Bogotá")]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div/div/div[3]/div/span[2]/button'))).click()
    
    time.sleep(random.uniform(2.0, 3.5))
    action.click(on_element = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div/div[3]/div/div[2]/div/div')))).perform()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Licores"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Sub-Categoría"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//label[text()="Ginebra"]'))).click()
    time.sleep(random.uniform(2.0, 3.5))
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    
    main_list = []
    main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'vtex-search-result-3-x-galleryItem')))
    
    
    for detail in main_box:
        nombre = detail.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-productBrand').text

        try:
            precio =  detail.find_element(By.CLASS_NAME, 'flex items-center').text
        except IndexError:
            precio =  detail.find_element(By.CLASS_NAME, 'vtex-product-price-1-x-sellingPrice--hasListPrice--dynamicF').text

        try:
            descuento = detail.find_element(By.CLASS_NAME, "olimpica-dinamic-flags-0-x-containerPercentageFlagDcto").text

        except NoSuchElementException:
            descuento = float('nan')

        main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Olimpica'})
        time.sleep(random.uniform(1.0, 1.5))
    
    
    driver.quit()
    
    df = pd.DataFrame(main_list)
    df['Descuento'] = df['Descuento'].apply(lambda x: ('-' + x[0] + '%') if not pd.isna(x) else float('nan'))
    driver.quit()
    print(f'{len(df)} {df.Store[0]} items was extracted')
    return df

# Merqueo
def merqueo_extract(driver):
    wait = WebDriverWait(driver, 50)
    driver.get('https://merqueo.com/bogota/super-ahorro/licores/ginebra')
    time.sleep(random.uniform(2.0, 3.5))
    
    main_list = []
    main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,"mq-product-card")))
    
    for detail in main_box:
        time.sleep(random.uniform(2.0, 2.5))      
        nombre = detail.find_element(By.CLASS_NAME, 'mq-product-title').text
        precio = detail.find_element(By.CLASS_NAME, 'mq-product-price').text

        try:
            descuento = detail.find_element(By.CLASS_NAME, "mq-percent-discount").text

        except NoSuchElementException:
            descuento = float('nan')

        main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Merqueo'})
        time.sleep(random.uniform(1.0, 1.5))
        
    df = pd.DataFrame(main_list)
    df['Descuento'] = df['Descuento'].apply(lambda x: ('-' + x[0] + '%') if not pd.isna(x) else float('nan'))
    print(f'{len(main_list)} {df.Store[0]} items was extracted')
    driver.quit()
    return df

# Carulla - Extacting the information by slicing (Price)
def carulla_extract(driver):
    driver.get('https://cava.carulla.com/vinos-y-licores/ginebra')
    wait = WebDriverWait(driver, 50)
    wait.until(EC.element_to_be_clickable((By.XPATH,'//button[text()="Sí"]'))).click()
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'exito-geolocation-3-x-cursorPointer'))).click()
    
    while 1:
        try:
            time.sleep(random.uniform(2.0,2.5))
            next_page1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Mostrar más"]')))
            next_page1.click()
            
            warn_click = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'exito-geolocation-3-x-cursorPointer'))).click()
            warn_click.click()
        except:
            break
        
    main_list = []
    main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtex-search-result-3-x-galleryItem")))
   
    for detail in main_box:
        nombre = detail.find_element(By.CLASS_NAME, "vtex-product-summary-2-x-productBrand").text
        
        try:
            precio =  detail.find_elements(By.CLASS_NAME, "exito-vtex-components-4-x-currencyContainer")[2].text
        except IndexError:
            precio =  detail.find_elements(By.CLASS_NAME, "exito-vtex-components-4-x-currencyContainer")[1].text
            
        try:
            descuento = detail.find_element(By.CLASS_NAME, "exito-vtex-components-4-x-badgeDiscount").text

        except NoSuchElementException:
            descuento = float('nan')

        main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Carulla'})
        time.sleep(random.uniform(1.0, 1.5))         
    
    df = pd.DataFrame(main_list)
    df['Descuento'] = df['Descuento'].apply(lambda x: (x.str[0] + x.str[1:]) if not pd.isna(x) else float('nan'))
    print(f'{len(df)} {df.Store[0]} items was extracted')
    driver.close()
    return df

if __name__ == "__main__":
    email_receiver = sys.argv[1]
    
    # Jumbo Retail
    driver = get_driver()
    data = jumbo_extract(driver)
    df_1 = data

    #Olimpica Retail
    driver = get_driver()
    data = olimpica_extract(driver)
    df_2 = data

    
    # Merqueo Retail
    driver = get_driver()
    data = merqueo_extract(driver)
    df_3 = data
    
#     # Carulla Retail
    driver = get_driver()
    data = carulla_extract(driver)
    df_4 = data
    
#     # Concat DataFrames
    pd.set_option('display.max_rows', None)
    df_full = pd.concat([df_1, df_2, df_3, df_4], axis=0, ignore_index=True)

    df_sale = df_full.query('Descuento.notnull()') \
                 .reset_index(drop=True)  
    
    # Send Email
    email_sender = os.environ.get("USER")
    email_password = os.environ.get("PASSWORD")

    msg = MIMEMultipart()
    msg['Subject'] = "Test Gin Discount Notificaton"
    msg['From'] = email_sender

    html_df = build_table(df_sale, 'blue_light', font_size='medium')
    html = """
    <html>
        <head><strong> Gin's on discounts for today! <strong></head>
      <body>
        {}
      </body>
    </html>
    """.format(html_df)

    part1 = MIMEText(html, 'html')
    msg.attach(part1)

    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
    server.login(email_sender, email_password)
    server.sendmail(email_sender, email_receiver, msg.as_string())
