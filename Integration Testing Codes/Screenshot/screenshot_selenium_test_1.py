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
driver.get("https://www.free-css.com/assets/files/free-css-templates/preview/page295/sbs/")

clickable_elements = driver.find_elements(By.XPATH, "//a | //button | //input[@type='submit']")

i = 0
for element in clickable_elements:
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

        element.screenshot("./img/image" + str(i) + ".png")
        i += 1
    except Exception as e:
        print(f"Failed to take a screenshot of element: {str(e)}")

time.sleep(1)
driver.quit()
