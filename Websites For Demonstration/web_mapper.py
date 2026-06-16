# PYTHON VERSION = 3.10.2
# PIP VERSION = 23.3.1

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
import math
import networkx as nx
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, legal, A0, landscape
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
import subprocess

total_clicks = 0
total_backs = 0
edges = []
root = True
mouse_speed = 1000
back_x = 72
back_y = 80


MY_SCREEN_X = 1920
MY_SCREEN_Y = 912
MY_SCREEN_Y_TABS = 106
TOTAL_Y_OF_MY_SCREEN = 1080
# Note: TOTAL_Y_OF_MY_SCREEN = MY_SCREEN_Y + MY_SCREEN_Y_TABS + taskbar_pixels

def scale_xab_to_xpq(xab,a,b,p,q):
    normalized = (xab-a+1)/(b-a+1)
    xpq = normalized*(q-p+1)+p-1
    return xpq

def check_if_visited_before(driver,visited_pages):
    if driver.current_url in visited_pages:
        return True
    else:
        return False

def check_if_dest_page(driver,dest_page):
    if dest_page.lower() in driver.title.lower():
        global edges
        global total_clicks
        edges.append((driver.title, 'End', {'label': str(total_clicks+1)}))
        return True
    else:
        return False

def process_page(driver,dest_page,visited_pages,prev_title):

    global edges
    global total_clicks
    global total_backs
    global root

    # print(f"Entered page: {driver.title}")
    if root:
        root = False
        edges.append(('Start', driver.title, {'label': str(total_clicks)}))
    else:
        edges.append((prev_title, driver.title, {'label': str(total_clicks)}))
    
    visited_before = check_if_visited_before(driver,visited_pages)
    if visited_before:
        return False
    
    is_dest_page = check_if_dest_page(driver,dest_page)
    if is_dest_page:
        return True
    
    visited_pages.append(driver.current_url)
    
    links = driver.find_elements(By.XPATH, "//a[@href] | //button")
    link_indices = set({})
    link_coords = []
    link_sizes = []
    screen_size_w = 0
    screen_size_h = 0
    for i, link in enumerate(links, start=0):
        with open("copy-main.js", "r") as file:
            js_code = file.read()
        features = driver.execute_script(js_code, link)
        coord = (features['button_center_x_coordinate'],features['button_center_y_coordinate'])
        sizes = (features['button_width'],features['button_height'])
        screen_size_w = features['w']
        screen_size_h = features['h']
        link_coords.append(coord)
        link_sizes.append(sizes)
        link_index_rank_pair = (i, i)
        link_indices.add(link_index_rank_pair)
                
    link_indices = sorted(link_indices)
    # print(link_indices)
    
    for rank, i in link_indices:
        
        link = links[i]
        # print(f"{i}. {link.get_attribute('innerHTML')}")
        # print(link.text)

        x, y = link_coords[i]

        # print(x,y)
        y = y / screen_size_h
        y = y * MY_SCREEN_Y
        y = y + MY_SCREEN_Y_TABS
        x = x / screen_size_w
        x = x * MY_SCREEN_X
        # pyautogui.moveTo(x, y, 0.5, pyautogui.easeInElastic)

        click_it = True

        if click_it:
            try:
                go_back = True
                cur_url = driver.current_url
                cur_title = driver.title
                link.click()
                total_clicks += 1
                if cur_url == driver.current_url:
                    go_back = False # If clicking the link leads to same as current page, do not trigger back button later
                WebDriverWait(driver, 10).until(EC.staleness_of(link))
                has_found = process_page(driver,dest_page,visited_pages,cur_title)
                if has_found:
                    return True
                if go_back:
                    # pyautogui.moveTo(28, 80, 0.5, pyautogui.easeInElastic)
                    driver.back()
                    total_backs += 1
                # print(f"Back in page: {driver.title}")
                links = driver.find_elements(By.XPATH, "//a[@href] | //button")
            except:
                print(f"{i}. {link.get_attribute('innerHTML')}")

    return False

def generate_report(has_found):
    G = nx.DiGraph()
    #G.add_nodes_from(['A', 'B', 'C', 'D'])

    global edges
    global total_clicks
    global total_backs
    G.add_edges_from(edges)
    # G.add_edges_from([('Start', 'Test Web', {'label': '0'}), ('Test Web', 'Bye', {'label': '1'}), ('Test Web', 'Hello World', {'label': '2'}), ('Hello World', 'Deeper', {'label': '3'}), ('Deeper', 'Even Deeper', {'label': '4'}), ('Even Deeper', 'Test Web', {'label': '5'}), ('Test Web', 'About Us', {'label': '6'}), ('About Us', 'About Us', {'label': '7'}), ('Test Web', 'Login', {'label': '8'}), ('Login', 'SignUp', {'label': '9'}), ('SignUp', 'Login', {'label': '10'}), ('Test Web', 'HSL', {'label': '11'}), ('HSL', 'New Page', {'label': '12'}), ('New Page', 'Bye', {'label': '13'}), ('New Page', 'Wiki', {'label': '14'}), ('Wiki', 'Test Web', {'label': '15'}), ('Test Web', 'Night', {'label': '16'}), ('Night', 'Day', {'label': '17'}), ('Day', 'Bye', {'label': '18'}), ('Night', 'Midnight', {'label': '19'}), ('Midnight', 'Midnight', {'label': '20'}), ('Midnight', 'Day', {'label': '21'}), ('Midnight', 'Dawn', {'label': '22'}), ('Dawn', 'Bye', {'label': '23'}), ('Night', 'Dawn', {'label': '24'})])

    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos=pos, with_labels=True, node_size=50, node_color='white', font_size=5, font_weight='bold', node_shape='s', alpha=0.5)

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_color='red', font_size=5)

    # plt.title('Graph')
    # plt.show()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    file_path = 'report.pdf'
    # c = canvas.Canvas(file_path, pagesize=letter)
    c = canvas.Canvas(file_path, pagesize=landscape(A0))

    text = ""

    if has_found:
        text = "Destination Page has been found! :D"
    else:
        text = "Destination Page was not found... :("
    

    # c.setFillColor(colors.grey)
    # c.setFont("Helvetica-Bold", 24)
    # c.drawString(250, 750, 'Report')

    # c.setFillColor(colors.black)
    # c.setFont("Helvetica", 14)
    # c.drawString(50, 720, "Verdict: " + text)
    # c.setFont("Helvetica", 10)
    # c.drawString(50, 700, "Total Clicks: " + str(total_clicks))
    # c.drawString(50, 680, "Total Backs: " + str(total_backs))


    graph_img = ImageReader(io.BytesIO(buffer.getvalue()))
    c.drawImage(graph_img, 0, 0, width=3200, height=2400)

    c.save()

    subprocess.Popen([file_path], shell=True)

def main():
    #url = input("Enter the URL you want to visit: ")
    url = "http://127.0.0.1:5500/Website%201/index.html"
    visited_pages = []
    #dest_page = input("Enter the destination page name: ") # Later Rewrite this to take task as input (maybe?)
    dest_page = "Adib"
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(url)
    
    try:
        has_found = process_page(driver,dest_page,visited_pages,driver.title)
    except:
        print("Errrrr")
        driver.quit()

    # print(total_clicks)
    # print(total_backs)
    # print(edges)
    generate_report(has_found)
    driver.quit()


if __name__ == "__main__":
    main()

#  ____  _____    _    ____     __  __ _____ 
# |  _ \| ____|  / \  |  _ \   |  \/  | ____|
# | |_) |  _|   / _ \ | | | |  | |\/| |  _|  
# |_| \_\_____/_/   \_\____/   |_|  |_|_____|

# ------------------------------
# -Required Dependencies:
# _______________________

# Before running the system, please ensure that you have python installed on your device and the following lines run:

# 1) from selenium import webdriver
# 2) from selenium.webdriver.common.by import By
# 3) from selenium.webdriver.support.ui import WebDriverWait
# 4) from selenium.webdriver.support import expected_conditions as EC
# 5) from ultralytics import YOLO
# 6) import pyautogui
# 7) import time
# 8) from sentence_transformers import SentenceTransformer, util
# 9) import networkx as nx
# 10) import matplotlib.pyplot as plt
# 11) from reportlab.pdfgen import canvas
# 12) from reportlab.lib.pagesizes import letter
# 13) from reportlab.lib import colors
# 14) from reportlab.lib.utils import ImageReader
# 15) import io
# 16) import subprocess
# 17) import pickle

# Some commands to install them are:

# 1) pip install selenium
# 2) pip install ultralytics
# 3) pip install pyautogui
# 4) pip install sentence_transformers
# 5) pip install networkx
# 6) pip install matplotlib
# 7) pip install reportlab
# 8) pip install pickle

# The rest of the packages: time, io, subprocess should be built-in your python installation.
# Check the versions at the top of this file


# ------------------------------
# -How To Run The System:
# _______________________

# 1)open CMD at the same location where main-system.py is and run the following command:
# 	> python main-system.py

# 2) wait for program to load

# 3) input the url of the website you want to test

# 4) input the title of the webpage you want the system to search for in the given website network

# 5) observe the simulation

# 6) analyze the report generated at the end of simulation

# ------------------------------
