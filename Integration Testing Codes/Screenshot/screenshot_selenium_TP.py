from selenium import webdriver
from PIL import Image

driver = webdriver.Chrome(executable_path="./chromedriver/chromedriver.exe")

driver.maximize_window()

driver.get("https://www.tutorialspoint.com/index.htm")

driver.refresh()

s = driver.find_element_by_xpath("//input[@class='gsc-input']")

location = s.location

size = s.size

driver.save_screenshot("screenshot_tutorialspoint.png")

x = location["x"]

y = location["y"]

height = location["y"] + size["height"]

width = location["x"] + size["width"]

imgOpen = Image.open("screenshot_tutorialspoint.png")

imgOpen = imgOpen.crop((int(x), int(y), int(width), int(height)))

imgOpen.save("screenshot_tutorialspoint.png")

driver.close()
