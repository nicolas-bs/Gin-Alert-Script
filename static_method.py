import sys
import os
import random
import pandas as pd
from time import sleep

# Selenium Libraries
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Email Libraries
from pretty_html_table import build_table
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl

# Configure Pandas
pd.options.display.float_format = "{:,.0f}".format

class GinScraper:
    def __init__(self):
        self.driver = self.get_driver()  # Create a new driver instance for each instance

    @staticmethod
    def get_driver():
        options = webdriver.ChromeOptions()
        options.binary_location = r"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument("--disable-notifications")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--disable-cache')
        options.add_argument("--headless=new")
        options.add_argument("--disable-popup-blocking")

        # Create and return a new ChromeDriver instance
        driver = webdriver.Chrome(options=options)
        print('Selenium driver instance created')
        return driver

    def jumbo_extract(self, liquor):
        driver = self.driver
        driver.get('https://www.tiendasjumbo.co')
        wait = WebDriverWait(driver, 50)
        action = ActionChains(driver)

        while True:
            try:
                licores_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "licores")]')))
                action.click(licores_link).perform()
                break
            except TimeoutException:
                slider_arrow = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'tiendasjumboqaio-jumbo-custom-pages-2-x-sliderRightArrow')))
                action.click(slider_arrow).perform()     

        sleep(random.uniform(2, 2.4))
        action.click(wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href,  '{liquor.lower()}')]")))).perform()

        main_list = []
        def extract_mainbox(main_box):

            for detail in main_box:
                nombre = detail.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-productBrand').text

                precio_element = detail.find_elements(By.CLASS_NAME, 'tiendasjumboqaio-jumbo-minicart-2-x-price')
                if len(precio_element) > 3:
                    precio = precio_element[1].text
                else:
                    precio = precio_element[0].text             
                try:
                    descuento = detail.find_element(By.CLASS_NAME, "tiendasjumboqaio-jumbo-minicart-2-x-containerPercentageFlag").text
                except NoSuchElementException:
                    descuento = float('nan')

                main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Jumbo'})
            return main_list

        number_of_pages = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'tiendasjumboqaio-jumbo-fetch-more-paginator-0-x-buttonPerPage')))
        sequential_list = list(range(1, len(number_of_pages) + 1))

        for page_number in sequential_list:
            main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtex-product-summary-2-x-container")))
            extract_mainbox(main_box)
            wait.until(EC.visibility_of_element_located((By.XPATH, f'//button[text()="{page_number}"]'))).click()
            sleep(random.uniform(2.5, 3.1))

        df = pd.DataFrame(main_list)
        df['Descuento'] = df['Descuento'].apply(lambda x: x.replace(' ', '') if not pd.isna(x) else float('nan'))
        print(f'{len(df)} {df.Store[0]} items were extracted')
        return df
    
    def olimpica_extract(self, liquor):
        driver = self.driver
        driver.get('https://www.olimpica.com/')
        wait = WebDriverWait(driver, 60)
        action = ActionChains(driver)

        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Cambiar"]'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Departamento"]'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "BOGO")]'))).click()
        
        sleep(random.uniform(2.0, 3.5))
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'css-1j9dihh-control'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Bogotá")]'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text() = "Elegir"]'))).click()
        
        sleep(random.uniform(2.0, 3.5))
        action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "supermercado")]')))).perform()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Licores"]'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Sub-Categoría"]'))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH,  f"//label[contains(text(), '{liquor.capitalize()}')]"))).click()
        sleep(random.uniform(4.0, 5.5))

        main_list = []
        def extract_info(main_box):
            for detail in main_box:  
                nombre = detail.find_element(By.CLASS_NAME,  'vtex-product-summary-2-x-productBrand').text
                precio =  detail.find_element(By.CLASS_NAME, 'vtex-product-price-1-x-sellingPrice--hasListPrice--dynamicF').text
                try:
                    descuento = detail.find_element(By.CLASS_NAME, "olimpica-dinamic-flags-0-x-containerPercentageFlagDcto").text
                except NoSuchElementException:
                    descuento = float('nan')       

                main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Olimpica'})
            return main_list
        
        sleep(random.uniform(4.0, 5.5))
        while True:
            last_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_height = driver.execute_script("return document.body.scrollHeight")
            sleep(random.uniform(3, 4.5))
            if new_height == last_height:
                break

        driver.execute_script("window.scrollTo(0, {});".format(last_height / 2))
        main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'vtex-search-result-3-x-galleryItem')))
        sleep(random.uniform(3.0, 3.5))
        extract_info(main_box)
    
        df = pd.DataFrame(main_list)
        df.drop_duplicates(inplace=True)
        df['Descuento'] = df['Descuento'].apply(lambda x: '-' + str(x).replace(' ', '') + '%' if not pd.isna(x) else float('nan'))
        print(f'{len(df)} {df.Store.iloc[0]} items were extracted')
        return df
    
    # Merqueo
    def merqueo_extract(self, liquor):
        driver = self.driver
        wait = WebDriverWait(driver, 50)
        action = ActionChains(driver)
        
        wait.until(EC.element_to_be_clickable((By.XPATH,  "//a[contains(@href, 'licores')]"))).click()
        sleep(random.uniform(2, 3.5))
    
        for _ in range(9):
            action.send_keys(Keys.PAGE_DOWN).perform()
            sleep(random.uniform(1.5, 2))
        
        boxes = driver.find_elements(By.XPATH, f'//section[contains(@id, "{liquor.lower()}")]')
        
        for box in boxes:
            main_list = []
            main_box = box.find_elements(By.CLASS_NAME, "mq-product-card-data")
            
            # Loop through main_box elements
            for detail in main_box:
                nombre = detail.find_element(By.CLASS_NAME, 'mq-product-title').text
                precio = detail.find_element(By.CLASS_NAME, 'mq-product-price').text
                try:
                    descuento = detail.find_element(By.CLASS_NAME, "mq-percent-discount").text
                except NoSuchElementException:
                    descuento = float('nan')
                main_list.append({
                    'Nombre': nombre,
                    'Descuento': descuento,
                    'Precio': precio,
                    'Store': 'Merqueo'})
                
        df = pd.DataFrame(main_list)
        df['Descuento'] = df['Descuento'].apply(lambda x: ('-' + x[0] + '%') if not pd.isna(x) else float('nan'))
        print(f'{len(main_list)} {df.Store[0]} items was extracted')
        return df

    # Carulla 
    def carulla_extract(self, liquor):
        driver = self.driver
        wait = WebDriverWait(driver, 50)
        action = ActionChains(driver)
        sleep(random.uniform(1,2))
        action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Sí"]')))).perform()
        sleep(random.uniform(1,2))
        action.click(wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href,  '{liquor.lower()}')]")))).perform()
        
        # Check if new window is created
        new_window = driver.window_handles[-1]  # Get the latest window handle
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(new_window)
        
        sleep(random.uniform(1,2))
        action.click(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-yiuvdt")))[0]).perform()
        sleep(random.uniform(1,2))
        action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Bogotá, D.c."]')))).perform()
        sleep(random.uniform(2,3))
        action.click(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-yiuvdt")))[1]).perform()
        sleep(random.uniform(2,3))
        action.click( wait.until(EC.element_to_be_clickable((By.XPATH,  '//div[contains(text(), "102")]')))).perform()
        sleep(random.uniform(2,3))
        action.click( wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Confirmar"]')))).perform()
        sleep(random.uniform(6,7))
        
        while True:
            try:
                driver.execute_script("arguments[0].scrollIntoView();",  wait.until(EC.visibility_of_element_located((By.XPATH, '//div[text()="Mostrar más"]'))))
                wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Mostrar más"]'))).click()
                sleep(random.uniform(1,2))
            except TimeoutException:
                break

        main_list = []
        main_box = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtex-search-result-3-x-galleryItem")))

        for detail in main_box:
            nombre = detail.find_element(By.CLASS_NAME, "vtex-product-summary-2-x-productBrand").text 
        
            precio_element =  detail.find_elements(By.CLASS_NAME, "exito-vtex-components-4-x-currencyContainer")
            if len(precio_element) > 2 :
                precio = precio_element[2].text
            else:
                precio = precio_element[1].text
            try:
                descuento = detail.find_element(By.CLASS_NAME, "exito-vtex-components-4-x-badgeDiscount").text
            except NoSuchElementException:
                descuento = float('nan')
            main_list.append({'Nombre': nombre, 'Descuento': descuento, 'Precio':precio, 'Store': 'Carulla'})
        
        df = pd.DataFrame(main_list)
        df['Descuento'] = df['Descuento'].apply(lambda x: x.replace(' ', '') if not pd.isna(x) else float('nan'))
        print(f'{len(df)} {df.Store[0]} items was extracted')
        return df
    
    # Exito
    def exito_extract(self, liquor):
        driver = self.driver
        driver.get('https://www.exito.com/')
        wait = WebDriverWait(driver, 50)
        action = ActionChains(driver)
        sleep(random.uniform(2, 4))
        action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Mercado"]')))).perform()
        sleep(random.uniform(2, 4))
        action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "licores")]')))).perform()
        sleep(random.uniform(2, 4))
        action.click(wait.until(EC.element_to_be_clickable((By.XPATH, f'//label[contains(text(), "{liquor.capitalize()}")]')))).perform()
        sleep(random.uniform(2, 3))
        driver.find_element(By.XPATH, '//button[text()="Aplicar filtros"]').click()
        sleep(random.uniform(7, 9))

        driver.execute_script("arguments[0].scrollIntoView();", wait.until(EC.visibility_of_element_located((By.XPATH, '//span[text()="Siguiente"]'))))
        main_list = []

        def extract_info(main_box):
            for detail in main_box:  
                nombre = detail.find_element(By.CSS_SELECTOR, 'h3[data-fs-product-card-title="true"]').text
                precio = detail.find_element(By.CSS_SELECTOR,  'div[data-fs-product-card-prices="true"]').text.split('\n')[-1]
                try:
                    descuento = detail.find_element(By.CSS_SELECTOR, 'span[data-percentage="true"]').text
                except NoSuchElementException:
                    descuento = descuento = float('nan')
                main_list.append({'Nombre': nombre, 'Precio': precio, 'Descuento': descuento, 'Store': 'Exito'})
            return main_list

        while True:
            try:
                main_box = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div[data-fs-product-card-content-image-price="true"]')))
                extract_info(main_box)
                sleep(random.uniform(2, 3))  # Add a small delay to allow the page to load
                next_button = driver.find_element(By.XPATH, '//span[text()="Siguiente"]')
                if next_button.is_enabled():
                    next_button.click()
                else:
                    break  # Exit the loop when "Siguiente" button is disabled
            except:
                break  # Exit the loop if there's a timeout

        sleep(random.uniform(2, 3))
        df = pd.DataFrame(main_list)
        df['Descuento'] = df['Descuento'] = df['Descuento'].apply(lambda x: f'-{x}' if not pd.isna(x) else float('nan'))
        print(f'{len(df)} {df.Store[0]} items were extracted')
        return df


    def extract_data(liquor):
        retailers = ["Jumbo", "Olimpica", "Merqueo", "Carulla"]
        return {retailer: getattr(GinScraper(), f"{retailer.lower()}_extract")(liquor) for retailer in retailers}


    def send_notification_email(df_sale, liquor, email_receiver):
        email_sender = os.getenv("EMAIL")
        email_password = os.getenv("PASSWORD")

        msg = MIMEMultipart()
        msg['Subject'] = f"{liquor} Discount Notification"
        msg['From'] = email_sender
        msg["To"] = email_receiver

        html_df = build_table(df_sale, 'blue_light', font_size='medium')
        html = f"""
        <html>
            <head><strong>{liquor} on discounts for today!<strong></head>
        <body>
            {html_df}
        </body>
        </html>
        """

        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            try:
                server.login(email_sender, email_password)
                server.sendmail(email_sender, email_receiver, msg.as_string())
                print(f"Email sent to {email_receiver} successfully.")
            except Exception as e:
                print(f"An error occurred while sending the email")


    def main(email_receiver, liquor):
        # Extract data from different retailers
        retail_data = GinScraper.extract_data(liquor)

        # Concatenate dataframes
        df_full = pd.concat(retail_data.values(), axis=0, ignore_index=True)

        # Clean and process data
        df_full['Precio'] = pd.to_numeric(df_full['Precio'].str.replace('[.$]', '', regex=True), downcast='float')

        # Filter and sort data
        df_sale = df_full.query('Descuento.notnull()') \
                            .sort_values(['Store', 'Precio'], ascending=[True, False]) \
                            .reset_index(drop=True)

        # Send the notification email
        GinScraper.send_notification_email(df_sale, liquor, email_receiver)

if __name__ == "__main__":
    load_dotenv()
    email_receiver = sys.argv[1]
    liquor = sys.argv[2]

    # Call the main method as a static method
    GinScraper.main(email_receiver, liquor)