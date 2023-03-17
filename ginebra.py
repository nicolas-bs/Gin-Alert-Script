"""
This email script alert aims to verify discount gins within three different Retail Stores in Colombia: Jumbo, Merquo, Carulla
"""
#! /usr/bin/python3
import pandas as pd
pd.options.display.float_format = "{:,.0f}".format
import time
from time import sleep
import random
import sys, os

# Selenium Library
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as BraveService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

# Email Library
from pretty_html_table import build_table
from dotenv import load_dotenv
load_dotenv()

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl

def get_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-notifications")
    options.add_argument('--disable-cache')
    options.add_argument("--headless=new")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    #driver_service = Service(ChromeDriverManager().install())
    #driver_service = Service('/Users/nicolasbenavides/Downloads/chromedriver')
    driver = webdriver.Chrome(service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()), options=options)
    print('Selenium driver instance created')
    return driver


# Jumbo
def jumbo_extract(driver):
    driver.get('https://www.tiendasjumbo.co')
    wait = WebDriverWait(driver, 40)
    action = ActionChains(driver)
    action.click(on_element  = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'tiendasjumboqaio-jumbo-custom-pages-2-x-sliderRightArrow')))).perform()
    action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Vinos y licores"]')))).perform()
    action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Ginebras"]')))).perform()
    
    for _ in range(6):
        driver.execute_script("window.scrollBy(0, 400);")
        sleep(random.uniform(2, 2.3))
    main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtex-product-summary-2-x-container")))
    
    main_list = []
    def extract_mainbox(main_box):
        
        for detail in main_box:
            nombre = detail.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-productBrand').text
                
            precio_element = detail.find_elements(By.CLASS_NAME, 'tiendasjumboqaio-jumbo-minicart-2-x-price')
            if len(precio_element) > 1:
                    precio = precio_element[1].text
            else:
                precio = precio_element[0].text             
            try:
                descuento = detail.find_element(By.CLASS_NAME, "tiendasjumboqaio-jumbo-minicart-2-x-containerPercentageFlag").text
            except NoSuchElementException:
                    descuento = float('nan')
                
            main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Jumbo'})
            
    extract_mainbox(main_box)
    sleep(random.uniform(2, 2.4))
    
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH ,'//button[text()="2"]'))).click()
        sleep(random.uniform(2, 2.4))
        main_box= wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtex-product-summary-2-x-container")))
        extract_mainbox(main_box)
    except:
         pass
    
    df = pd.DataFrame(main_list)
    df = df.drop_duplicates()
    df['Descuento'] = df['Descuento'].str.replace(' ', '', regex=True)
    print(f'{len(df)} {df.Store[0]} items was extracted')
    driver.quit()
    return df

def olimpica_extract(driver):
    driver.get('https://www.olimpica.com/')
    wait = WebDriverWait(driver, 30)
    action = ActionChains(driver)

    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Departamento"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "BOGO")]'))).click()
    
    sleep(random.uniform(2.0, 3.5))
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Ciudad"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Bogotá")]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div/div/div[3]/div/span[2]/button'))).click()
    
    sleep(random.uniform(2.0, 3.5))
    action.click(on_element = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div/div[3]/div/div[2]/div/div')))).perform()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Licores"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Sub-Categoría"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//label[text()="Ginebra"]'))).click()
    sleep(random.uniform(2.0, 3.5))

    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 400);")
        sleep(random.uniform(2, 2.5))
    main_box = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'vtex-search-result-3-x-galleryItem')))
    
    sleep(random.uniform(2.0, 3.5))
    main_list = []
    for detail in main_box:  
        nombre = detail.find_element(By.CLASS_NAME,  'vtex-product-summary-2-x-productBrand').text
        precio =  detail.find_element(By.CLASS_NAME, 'vtex-product-price-1-x-sellingPrice--hasListPrice--dynamicF').text
        try:
            descuento = detail.find_element(By.CLASS_NAME, "olimpica-dinamic-flags-0-x-containerPercentageFlagDcto").text
        except NoSuchElementException:
            descuento = float('nan')       

        main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Olimpica'})
    
    df = pd.DataFrame(main_list)
    df['Descuento'] = df['Descuento'].apply(lambda x: '-' + str(x).replace(' ', '') + '%' if not pd.isna(x) else float('nan'))
    driver.quit()
    print(f'{len(df)} {df.Store[0]} items was extracted')
    return df

# Merqueo
def merqueo_extract(driver):
    wait = WebDriverWait(driver, 50)
    action = ActionChains(driver)
    driver.get('https://merqueo.com/bogota/super-ahorro/licores/ginebra')
    time.sleep(random.uniform(2.0, 3.5))

    for _ in range(2):
        driver.execute_script("window.scrollBy(0, 450);")
        time.sleep(random.uniform(1.5, 2))
    
    main_list = []
    main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,"mq-product-card")))
    
    for detail in main_box:    
        nombre = detail.find_element(By.CLASS_NAME, 'mq-product-title').text
        precio = detail.find_element(By.CLASS_NAME, 'mq-product-price').text
        try:
            descuento = detail.find_element(By.CLASS_NAME, "mq-percent-discount").text

        except NoSuchElementException:
            descuento = float('nan')

        main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Merqueo'})
        
    df = pd.DataFrame(main_list)
    df['Descuento'] = df['Descuento'].apply(lambda x: ('-' + x[0] + '%') if not pd.isna(x) else float('nan'))
    print(f'{len(main_list)} {df.Store[0]} items was extracted')
    driver.quit()
    return df

# Carulla - Extacting the information by slicing (Price)

def carulla_extract(driver):
    driver.get('https://cava.carulla.com/')
    wait = WebDriverWait(driver, 50)
    action = ActionChains(driver)
    
    sleep(random.uniform(1,2))
    action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Sí"]')))).perform()
    sleep(random.uniform(1,2))
    action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Ginebras"]')))).perform()
    new_window = driver.window_handles[-1]  # Get the latest window handle
    driver.close()
    driver.switch_to.window(new_window)

    action.click(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-yiuvdt")))[0]).perform()
    action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Bogotá, D.c."]')))).perform()
    sleep(random.uniform(1,2))
    action.click(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-yiuvdt")))[1]).perform()
    action.click( wait.until(EC.element_to_be_clickable((By.XPATH,  '//div[contains(text(), "102")]')))).perform()
    action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Confirmar"]')))).perform()
    sleep(random.uniform(2,3))
    
    for _ in range(2):
        driver.execute_script("window.scrollBy(0, 450);")
        sleep(random.uniform(2, 2.5))

    while True:
        try:
            action.click(EC.element_to_be_clickable((By.XPATH, '//div[text()="Mostrar más"]')).__call__(driver)).perform()
            driver.execute_script("window.scrollBy(0, 400);")
            sleep(random.uniform(2, 2.5))
            break
        except:
            break  
    main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtex-search-result-3-x-galleryItem")))
        
    main_list = []
    for detail in main_box:
        nombre = detail.find_element(By.CLASS_NAME, "vtex-product-summary-2-x-productBrand").text 
      
        precio_element =  detail.find_elements(By.CLASS_NAME, "exito-vtex-components-4-x-currencyContainer")
        if len(precio_element) == 3:
            precio = precio_element[2].text
        else:
            precio = precio_element[1].text
        try:
            descuento = detail.find_element(By.CLASS_NAME, "exito-vtex-components-4-x-badgeDiscount").text
        except NoSuchElementException:
            descuento = float('nan')

        main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Carulla'})       
    
    df = pd.DataFrame(main_list)
    df['Descuento'] = df['Descuento'].apply(lambda x: (x.str[0] + x.str[1:]) if not pd.isna(x) else float('nan'))
    print(f'{len(df)} {df.Store[0]} items was extracted')
    driver.quit()
    return df


# Exito
def exito_extract(driver):
    driver.get('https://www.exito.com/')
    wait = WebDriverWait(driver, 60)
    action = ActionChains(driver)
    sleep(random.uniform(1,2))
    action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Mercado"]')))).perform()
    sleep(random.uniform(1,2))
    action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Licores"]')))).perform()
    sleep(random.uniform(1,2))
    action.click(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-yiuvdt")))[0]).perform()
    action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Bogotá, D.c."]')))).perform()
    sleep(random.uniform(1,2))
    action.click(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-yiuvdt")))[1]).perform()
    action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Colina")]')))).perform()
    action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Confirmar"]')))).perform()
    sleep(random.uniform(2,3))
    action.click( wait.until(EC.presence_of_element_located((By.XPATH, '//div[text()="Sub-categoría"]')))).perform()
    sleep(random.uniform(2,3))
    action.click( wait.until(EC.presence_of_element_located((By.ID, 'category-3-ginebra')))).perform()
    sleep(random.uniform(2,3))
    for _ in range(4):
        driver.execute_script("window.scrollBy(0, 500);")
        sleep(random.uniform(2, 3))
    
    while True:
        try:
            action.click(EC.element_to_be_clickable((By.XPATH, '//div[text()="Mostrar más"]')).__call__(driver)).perform()
            driver.execute_script("window.scrollBy(0, 400);")
            sleep(random.uniform(2, 3))
            break
        except:
            break
    
    main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtex-search-result-3-x-galleryItem")))
    
    main_list = []
    for detail in main_box: 
        nombre = detail.find_element(By.CLASS_NAME, "vtex-store-components-3-x-productBrand ").text
        
        precio_elements = detail.find_elements(By.CLASS_NAME, "exito-vtex-components-4-x-currencyContainer")
        if len(precio_elements) > 2:
            precio = precio_elements[2].text
        else:
            precio = precio_elements[1].text
        try:
            descuento = detail.find_element(By.CLASS_NAME, "exito-vtex-components-4-x-badgeDiscount").text
        except NoSuchElementException:
            descuento = float('nan')

        main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Exito'})
     
    df = pd.DataFrame(main_list)
    print(f'{len(df)} {df.Store[0]} items was extracted')
    df['Descuento'] = df['Descuento'] = df['Descuento'].str.replace(' ', '', regex=True)
    driver.quit() 
    return df
    
if __name__ == "__main__":
    email_receiver = sys.argv[1]
    
    # Jumbo Retail
    driver = get_driver()
    df_1 = jumbo_extract(driver)

    # Olimpica Retail
    driver = get_driver()
    df_2 = olimpica_extract(driver)
    
    # Merqueo Retail
    driver = get_driver()
    df_3 = merqueo_extract(driver)
    
    # Carulla Retail
    driver = get_driver()
    df_4 = carulla_extract(driver)

    # Exito Retail
    driver = get_driver()
    df_5 = exito_extract(driver)
    
   # Concat DataFrames
    pd.set_option('display.max_rows', None)
    
    df_full = pd.concat([df_1, df_2, df_3, df_4, df_5], axis=0, ignore_index=True)
    
    df_full['Precio'] = pd.to_numeric(df_full['Precio'].str.replace('[.$]', '', regex=True), downcast='float')

    df_sale = df_full.query('Descuento.notnull()') \
                    .sort_values(['Store','Precio'], ascending=[True, False]) \
                    .reset_index(drop=True)
    
    # Send Email
    email_sender = os.environ.get("EMAIL")
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
