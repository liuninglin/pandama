from config.settings.config_common import \
    PANDAMA_DOMAIN, PANDAMA_PDP_PREURL, \
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, \
    CHROMEDRIVER_PATH, GOOGLE_CHROME_BIN 
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import boto3
import boto3.s3

class ScreenshotProcessor:
    def pdp_screenshot(order_id, product_number):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = GOOGLE_CHROME_BIN
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')
        # driver = webdriver.Chrome(options=chrome_options, executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
    
        url = PANDAMA_DOMAIN + PANDAMA_PDP_PREURL + "?product_number=" + str(product_number)
        driver.get(url)
        driver.set_window_size(width=500, height=900)
        ele=driver.find_element(by=By.CLASS_NAME, value="page-content-wrapper")
        total_height = ele.size["height"]+100
        driver.set_window_size(500, total_height)
        
        driver.save_screenshot("ss.png")
        
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-2')
        s3.upload_file("ss.png", AWS_STORAGE_BUCKET_NAME, ('pdp_screens/' + str(order_id) + '_' + str(product_number) + ".png"))

        return str(order_id) + '_' + str(product_number) + ".png" 
