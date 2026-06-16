from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

chrome_location = "./chrome/chrome.exe"
chromedriver_location = "./chromedriver/chromedriver.exe"

options = webdriver.ChromeOptions()
options.binary_location = chrome_location

chrome_service = Service(chromedriver_location)

driver = webdriver.Chrome(service=chrome_service, options=options)
driver.maximize_window()
# driver.get("https://tutorialsninja.com/demo")
# driver.get("https://books.toscrape.com/")
driver.get("https://gearsforears.com/collections/wireless-earphone")


search_button = driver.find_elements(By.XPATH, "//a[@class='hidden-product-link']")

i = 0
for x in search_button:
    x.screenshot("./img/image" + str(i) + ".png")
    i += 1

time.sleep(1)

driver.quit()
