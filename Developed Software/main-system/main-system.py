# PYTHON VERSION = 3.10.2
# PIP VERSION = 23.3.1

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ultralytics import YOLO
import pandas as pd
import pyautogui
import numpy as np
import time
import math
import random
from sentence_transformers import SentenceTransformer, util
import networkx as nx
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
import subprocess
import pickle
with open('features.txt', 'r') as file:
    features_text = file.read()
with open('normalize_these.txt', 'r') as file:
    normalize_these = file.read()
with open('order_model.pkl' , 'rb') as f:
    order_model = pickle.load(f)
with open('scaler.pkl' , 'rb') as f:
    scaler = pickle.load(f)

features_from_text = features_text.split('\n')
features_from_text.pop()

normalize_these_from_text = normalize_these.split('\n')
normalize_these_from_text.pop()

total_clicks = 0
total_backs = 0
edges = []
root = True
mouse_speed = 1000
back_x = 72
back_y = 80

tween_counts = [0, 0]
tween_limits = [3, 1]
tween_limits2 = [2, 1]
GLOBAL_T = 0
WANDER_T = 1

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

MY_SCREEN_X = 1920
MY_SCREEN_Y = 912
MY_SCREEN_Y_TABS = 106
TOTAL_Y_OF_MY_SCREEN = 1080
# Note: TOTAL_Y_OF_MY_SCREEN = MY_SCREEN_Y + MY_SCREEN_Y_TABS + taskbar_pixels

REGULAR_DELAY = 0.75
BACK_DELAY = 1

WANDERING_AMPLITUDE_LOW = 0.1
WANDERING_AMPLITUDE_HIGH = 0.4
WANDERING_LAMBDA = 3
WANDERING_CHANCE = 30

def move_humanly(end_pos, speed, wandering=False):
    current_mouse = pyautogui.position()
    start_x, start_y = current_mouse
    end_x, end_y = end_pos

    distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
    actual_speed = 0
    if wandering: actual_speed = speed
    else: actual_speed = speed + random.randint(-200, 200)
    duration = distance / actual_speed

    steps = int(distance / 10) + 5
    if steps < 10: steps = 10
    
    curve_offset = 0
    i_T = -1
    if wandering:
        curve_offset = random.choice([random.randint(-100, -50), random.randint(50, 100)])
        i_T = WANDER_T
    else:
        curve_offset = random.choice([random.randint(-150, -100), random.randint(100, 150)])
        i_T = GLOBAL_T
    # 500 too much, 250 too obvious, 150 still high, 100 looks good but maybe too low?
    # need to set it randomly and never too low, and based on distance, proportional to distance
    # print("curve offset = "+str(curve_offset))

    # print(start_x,start_y)
    # print(end_x,end_y)
    # print(actual_speed,distance,duration)
    #print(steps,duration)

    # TWEENING LOGIC
    tween_rand = random.randint(1,3)
    #print("tween_rand")
    #print(tween_rand)
    #print("i_T")
    #print(i_T)
    tween_type = -1
    if tween_rand==2:
        if tween_counts[i_T]>=tween_limits[i_T]:
            tween_type = 1
        elif tween_counts[i_T]>=tween_limits2[i_T]:
            tween_type = 3
        else:
            tween_type = 2
        tween_counts[i_T]=tween_counts[i_T]+1
    else:
        tween_type = 1
    
    for i in range(steps):
        t = i / (steps - 1)

        # TWEENING
        if tween_type==2:
            t = pyautogui.easeInOutElastic(t)
        elif tween_type==3:
            t = pyautogui.easeInOutBounce(t)
        else:
            t = pyautogui.easeInOutQuad(t)

        #t = pyautogui.easeOutQuad(t)
        #t = pyautogui.easeInQuad(t)
        #t = pyautogui.easeInOutQuad(t) # W ALLx tween_type = 1
        #t = pyautogui.easeInElastic(t)
        #t = pyautogui.easeOutElastic(t)
        #t = pyautogui.easeInOutElastic(t) # W 2x tween_type = 2
        #t = pyautogui.easeInBounce(t)
        #t = pyautogui.easeOutBounce(t)
        #t = pyautogui.easeInOutBounce(t) # W 1x tween_type = 3

        target_x = start_x + (end_x - start_x) * t
        target_y = start_y + (end_y - start_y) * t
        curve = np.sin(t * np.pi) * curve_offset
        jitter = random.uniform(-1, 1)
        pyautogui.moveTo(target_x + jitter, target_y + curve + jitter)
        # print(duration / steps)
        time.sleep(duration / steps)

def get_wander_coord(c,bounding,variance):
    dc = bounding * variance
    low = max(c-dc,0)
    high = min(c+dc,bounding)
    max_length = max(c-low,high-c)
    return random.uniform(low,high),max_length

def scale_xab_to_xpq(xab,a,b,p,q):
    normalized = (xab-a+1)/(b-a+1)
    xpq = normalized*(q-p+1)+p-1
    return xpq

def wander(chance=WANDERING_CHANCE): # chance of wandering in %
    dice_roll = random.randint(1,100)
    if dice_roll>chance:
        return
    print("wandering")
    #print(tween_counts[WANDER_T])

    variance = random.uniform(WANDERING_AMPLITUDE_LOW,WANDERING_AMPLITUDE_HIGH)

    current_mouse = pyautogui.position()
    x, y = current_mouse
    end_x,max_x_length = get_wander_coord(x,MY_SCREEN_X,variance/WANDERING_LAMBDA)
    end_y,max_y_length = get_wander_coord(y,TOTAL_Y_OF_MY_SCREEN,variance/WANDERING_LAMBDA)

    distance = math.sqrt((end_x - x)**2 + (end_y - y)**2)
    min_distance = 0
    max_distance = math.sqrt((max_x_length)**2 + (max_y_length)**2)

    min_speed = mouse_speed*WANDERING_AMPLITUDE_LOW
    max_speed = mouse_speed*WANDERING_AMPLITUDE_HIGH

    speed = scale_xab_to_xpq(distance,min_distance,max_distance,min_speed,max_speed)

    #print(end_x,end_y,speed)
    move_humanly((end_x,end_y),speed,True)

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

def get_button_identification_coords(driver):
    driver.save_screenshot("ss.png")
    
    model=YOLO("best.pt")
    results=model.predict(source="ss.png",show=False,conf=0.25)

    #result = results[0]
    #result.save("predicted_image.jpg")

    coords = []

    for xyxy in results[0].boxes.xyxy:
        x = (xyxy[0] + xyxy[2]) / 2
        x = (x + 1) / 1920
        x = (x * 1537) - 1

        y = (xyxy[1] + xyxy[3]) / 2
        y = (y + 1) / 913
        y = (y * 732) - 1

        coord = ( x, y )
        coords.append( coord )

    return coords

def get_button_ordering_rank(features):
    global order_model
    global scaler
    global features_from_text
    global normalize_these_from_text

    #print(features)

    # button_center_x_coordinate = features['button_center_x_coordinate']
    # features['button_center_x_coordinate'] = features['button_center_x_coordinate'] / features['w']
    # button_center_y_coordinate = features['button_center_y_coordinate']
    # features['button_center_y_coordinate'] = features['button_center_y_coordinate'] / features['h']

    features_df = pd.DataFrame([features])
    features_df[normalize_these_from_text] = scaler.transform(features_df[normalize_these_from_text])

    # input_data_init = []
    # for fet in features_from_text:
    #     # print(f"fet = {fet}")
    #     val = features[fet]
    #     input_data_init.append(val)
    # input_data = [input_data_init]

    input_data = features_df[features_from_text]
    pred = order_model.predict(input_data)
    # print(f"Prediction: {pred}")

    # features['button_center_x_coordinate'] = button_center_x_coordinate
    # features['button_center_y_coordinate'] = button_center_y_coordinate

    # return random.random()
    return pred[0]

def semantic_similarity(sentence1, sentence2, model_name="paraphrase-MiniLM-L12-v2"):
    model = SentenceTransformer(model_name)

    embeddings1 = model.encode(sentence1, convert_to_tensor=True)
    embeddings2 = model.encode(sentence2, convert_to_tensor=True)

    similarity_score = util.pytorch_cos_sim(embeddings1, embeddings2)[0][0].item()

    return similarity_score

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
    
    wander()
    time.sleep(REGULAR_DELAY)
    
    visited_before = check_if_visited_before(driver,visited_pages)
    if visited_before:
        return False
    
    is_dest_page = check_if_dest_page(driver,dest_page)
    if is_dest_page:
        wander(100)
        time.sleep(BACK_DELAY)
        return True
    
    visited_pages.append(driver.current_url)
    
    coords = get_button_identification_coords(driver)
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
        error_tolerance = 5
        for img_coord in coords:
            if abs(img_coord[0]-coord[0]) <= error_tolerance and abs(img_coord[1]-coord[1]) <= error_tolerance:
                rank_val = get_button_ordering_rank(features)
                link_index_rank_pair = (rank_val, i)
                link_indices.add(link_index_rank_pair)

    link_indices = sorted(link_indices, reverse = True)
    # print(link_indices)
    
    for rank, i in link_indices:
        
        link = links[i]
        # print(f"{i}. {link.get_attribute('innerHTML')}")
        # print(link.text)

        x, y = link_coords[i]
        width, height = link_sizes[i]
        
        # Target coord should within 80% inner of button
        # 0.5 cuz center theke dui pashe jabe so we need to half it duh
        # thats why 0.8 * 0.5 = 0.4 written
        width = width * MY_SCREEN_X * 0.4
        height = height * MY_SCREEN_Y * 0.4
        
        # To randomize target endpoint
        vx = random.uniform(-width,width)
        vy = random.uniform(-height,height)

        # print(x,y)
        y = y / screen_size_h
        y = y * MY_SCREEN_Y
        y = y + MY_SCREEN_Y_TABS
        x = x / screen_size_w
        x = x * MY_SCREEN_X
        # pyautogui.moveTo(x, y, 0.5, pyautogui.easeInElastic)
        wander()
        move_humanly((x+vx, y+vy),mouse_speed)

        click_it = False
        sameness = semantic_similarity(link.text, dest_page)
        # print(f"Semantic similarity between '{link.text}' and '{dest_page}': {sameness}")
        if sameness >= 0.4:
            click_it = True

        if click_it:
            try:
                # time.sleep(REGULAR_DELAY)
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
                    wander()
                    move_humanly((back_x,back_y),mouse_speed)
                    time.sleep(REGULAR_DELAY)
                    driver.back()
                    time.sleep(BACK_DELAY)
                    wander()
                    total_backs += 1
                # print(f"Back in page: {driver.title}")
                links = driver.find_elements(By.XPATH, "//a[@href] | //button")
            except:
                print(f"{i}. {link.get_attribute('innerHTML')}")

    wander()
    time.sleep(REGULAR_DELAY)
    
    return False

def generate_report(has_found):
    G = nx.DiGraph()
    #G.add_nodes_from(['A', 'B', 'C', 'D'])

    global edges
    global total_clicks
    global total_backs
    G.add_edges_from(edges)
    # G.add_edges_from([('Start', 'Test Web', {'label': '0'}), ('Test Web', 'Bye', {'label': '1'}), ('Test Web', 'Hello World', {'label': '2'}), ('Hello World', 'Deeper', {'label': '3'}), ('Deeper', 'Even Deeper', {'label': '4'}), ('Even Deeper', 'Test Web', {'label': '5'}), ('Test Web', 'About Us', {'label': '6'}), ('About Us', 'About Us', {'label': '7'}), ('Test Web', 'Login', {'label': '8'}), ('Login', 'SignUp', {'label': '9'}), ('SignUp', 'Login', {'label': '10'}), ('Test Web', 'HSL', {'label': '11'}), ('HSL', 'New Page', {'label': '12'}), ('New Page', 'Bye', {'label': '13'}), ('New Page', 'Wiki', {'label': '14'}), ('Wiki', 'Test Web', {'label': '15'}), ('Test Web', 'Night', {'label': '16'}), ('Night', 'Day', {'label': '17'}), ('Day', 'Bye', {'label': '18'}), ('Night', 'Midnight', {'label': '19'}), ('Midnight', 'Midnight', {'label': '20'}), ('Midnight', 'Day', {'label': '21'}), ('Midnight', 'Dawn', {'label': '22'}), ('Dawn', 'Bye', {'label': '23'}), ('Night', 'Dawn', {'label': '24'})])

    pos = pos = nx.circular_layout(G)
    nx.draw(G, pos=pos, with_labels=True, node_size=200, node_color='white', font_size=7, font_weight='bold', node_shape='s', alpha=0.5)

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_color='red', font_size=7)

    # plt.title('Graph')
    # plt.show()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    file_path = 'report.pdf'
    c = canvas.Canvas(file_path, pagesize=letter)

    text = ""

    if has_found:
        text = "Destination Page has been found! :D"
    else:
        text = "Destination Page was not found... :("
    

    c.setFillColor(colors.grey)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(250, 750, 'Report')

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 14)
    c.drawString(50, 720, "Verdict: " + text)
    c.setFont("Helvetica", 10)
    c.drawString(50, 700, "Total Clicks: " + str(total_clicks))
    c.drawString(50, 680, "Total Backs: " + str(total_backs))


    graph_img = ImageReader(io.BytesIO(buffer.getvalue()))
    c.drawImage(graph_img, 0, 0, width=620, height=600)

    c.save()

    subprocess.Popen([file_path], shell=True)

def test_wandering():
    print(f"mouse_speed={mouse_speed}")
    timer = time.time()
    wander()
    print(time.time()-timer)
    timer = time.time()
    #time.sleep(2)
    wander()
    print(time.time()-timer)
    timer = time.time()
    #time.sleep(2)
    wander()
    print(time.time()-timer)
    timer = time.time()
    #time.sleep(2)
    wander()
    print(time.time()-timer)
    timer = time.time()
    #time.sleep(2)
    wander()
    print(time.time()-timer)

def main():
    #url = input("Enter the URL you want to visit: ")
    url = "http://127.0.0.1:5500/Websites%20For%20Demonstration/Website%202/index.html"
    visited_pages = []
    #dest_page = input("Enter the destination page name: ") # Later Rewrite this to take task as input (maybe?)
    dest_page = "Tuna"
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(url)
    
    #try:
    has_found = process_page(driver,dest_page,visited_pages,driver.title)
    #except:
        #print("Errrrr")
        #driver.quit()

    print("tween_counts")
    print(tween_counts)
    # print(total_clicks)
    # print(total_backs)
    # print(edges)
    #generate_report(has_found)
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
