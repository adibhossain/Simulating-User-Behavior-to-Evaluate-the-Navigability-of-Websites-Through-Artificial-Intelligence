from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
with open('features.txt', 'r') as file:
    features_text = file.read()
with open('order_model.pkl' , 'rb') as f:
    order_model = pickle.load(f)

features_from_text = features_text.split('\n')
features_from_text.pop()

def list_and_choose_links(driver):
    links = driver.find_elements(By.XPATH, "//a[@href] | //button")
    print("Clickable Links/Buttons:")
    for i, link in enumerate(links, start=1):
        print(f"{i}. {link.text}")
    choice = input("Enter the number corresponding to the link/button you want to click (or 'q' to quit): ")
    if choice.lower() == 'q':
        return None
    try:
        choice_index = int(choice) - 1
        if choice_index >= 0 and choice_index < len(links):
            return links[choice_index]
        else:
            print("Invalid choice! Please enter a valid number.")
            return list_and_choose_links(driver)
    except ValueError:
        print("Invalid choice! Please enter a valid number.")
        return list_and_choose_links(driver)


def main():
    # myset = set({})
    # myset.add((1.5,2))
    # myset.add((1,3))
    # myset.add((1.665,9))
    # myset.add((1.509,5))
    # myset.add((1.5,1))
    # myset.add((4.5,8))

    # myset = sorted(myset, reverse = True)

    # print(myset)

    # print((1,3) in myset)
    # print((1.5,3) in myset)
    url = input("Enter the URL you want to visit: ")
    driver = webdriver.Firefox()
    driver.get(url)

    with open("copy-main.js", "r") as file:
        js_code = file.read()

    clickable_element = list_and_choose_links(driver)


    features = driver.execute_script(js_code, clickable_element)

    input_data_init = []
    for fet in features_from_text:
        # print(f"fet = {fet}")
        val = features[fet]
        input_data_init.append(val)
    input_data = [input_data_init]
    pred = order_model.predict(input_data)
    print(f"Prediction: {pred}")

    print(features)
    print(f"button_contrast_with_background: {features['button_contrast_with_background']}")

    any = input("Input anything to quit: ")
    driver.quit()

if __name__ == "__main__":
    main()
