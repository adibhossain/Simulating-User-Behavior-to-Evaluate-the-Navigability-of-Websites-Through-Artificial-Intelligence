from selenium import webdriver
from selenium.webdriver.common.by import By
import pyautogui
import time


def list_links(driver):
    links = driver.find_elements(By.XPATH, "//a[@href] | //button")
    print("Clickable Links/Buttons:")
    for i, link in enumerate(links, start=1):
        print(f"{i}. {link.text}")
    return links


def choose_link(links):
    while True:
        choice = input(
            "Enter the number corresponding to the link/button you want to click (or 'q' to quit): "
        )
        if choice.lower() == "q":
            return None
        try:
            choice_index = int(choice) - 1
            if choice_index >= 0 and choice_index < len(links):
                return links[choice_index]
            else:
                print("Invalid choice! Please enter a valid number.")
        except ValueError:
            print("Invalid choice! Please enter a valid number.")


def main():
    driver = webdriver.Firefox()
    while True:
        url = input("Enter the URL you want to visit (or 'q' to quit): ")
        if url.lower() == "q":
            break
        driver.get(url)
        while True:
            links = list_links(driver)
            if not links:
                print("No clickable links/buttons found on this page.")
                break
            chosen_link = choose_link(links)
            if chosen_link is None:
                break
            
            # location = chosen_link.location_once_scrolled_into_view
            with open("copy-main.js", "r") as file:
                js_code = file.read()
            features = driver.execute_script(js_code, chosen_link)
            x, y = (features['button_center_x_coordinate'],features['button_center_y_coordinate'])
            print(features['w'],features['h'])
            print(x,y)
            
            y = y / 731
            y = y * 912
            y = y + 106
            x = x / 1536
            x = x * 1920
            
            print(pyautogui.position())
            pyautogui.moveTo(x, y, duration=0.5)
            print(pyautogui.position())
            time.sleep(1)
            
            # pyautogui.click()
            print(f"Clicked on {chosen_link.text}")
            
            time.sleep(
                3
            )
    driver.quit()

if __name__ == "__main__":
    main()
