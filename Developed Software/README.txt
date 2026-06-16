------------------------------
-Required Dependencies:
_______________________

Before running the system, please ensure that you have python installed on your device and the following lines run:

1) from selenium import webdriver
2) from selenium.webdriver.common.by import By
3) from selenium.webdriver.support.ui import WebDriverWait
4) from selenium.webdriver.support import expected_conditions as EC
5) from ultralytics import YOLO
6) import pyautogui
7) import time
8) from sentence_transformers import SentenceTransformer, util
9) import networkx as nx
10) import matplotlib.pyplot as plt
11) from reportlab.pdfgen import canvas
12) from reportlab.lib.pagesizes import letter
13) from reportlab.lib import colors
14) from reportlab.lib.utils import ImageReader
15) import io
16) import subprocess
17) import pickle

Some commands to install them are:

1) pip install selenium
2) pip install ultralytics
3) pip install pyautogui
4) pip install sentence_transformers
5) pip install networkx
6) pip install matplotlib
7) pip install reportlab
8) pip install pickle

The rest of the packages: time, io, subprocess should be built-in your python installation.


------------------------------
-How To Run The System:
_______________________

1)open CMD at the same location where main-system.py is and run the following command:
	> python main-system.py

2) wait for program to load

3) input the url of the website you want to test

4) input the title of the webpage you want the system to search for in the given website network

5) observe the simulation

6) analyze the report generated at the end of simulation

------------------------------