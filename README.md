# Human-Like Autonomous Web Navigation Agent

An autonomous agent that explores a website the way a human would — moving the mouse along curved, jittered, eased paths — and tries to reach a target page on its own. It combines **computer vision**, a **machine-learning ranking model**, and **semantic text matching** to decide *which* button to click and *in what order*, then produces a navigation-graph report.

This repository is the codebase for a thesis project. It contains the final runnable system plus all the supporting code used to build, train, and test it.

---

## How It Works

For each page the agent lands on, it runs this pipeline:

1. **Screenshot + button detection** — Selenium captures the page; a **YOLO** model (`best.pt`) detects clickable button regions in the image.
2. **Feature extraction** — `copy-main.js` is injected via Selenium to pull ~43 features per `<a>`/`<button>` (size, color, contrast, position, text style, neighbor density, etc.).
3. **Button ordering** — detected buttons are matched to DOM elements, then a trained model (`order_model.pkl`, with `scaler.pkl` for normalization) ranks the click order.
4. **Semantic relevance** — `sentence-transformers` (`paraphrase-MiniLM-L12-v2`) compares each button's text to the target page name; buttons scoring ≥ 0.4 are clicked.
5. **Human-like motion** — `pyautogui` moves the mouse with Bézier-style curves, random tweening (elastic/bounce/quad easing), jitter, and occasional idle "wandering."
6. **Recursive search** — clicks, descends into the new page, backtracks with the browser Back button, and repeats until the target page title is found or the network is exhausted.
7. **Report** — builds a directed navigation graph with `networkx` and writes a `report.pdf` (verdict, total clicks, total backs, graph image).

---

## Repository Layout

```
.
├── Developed Software/
│   └── main-system/              # ← THE FINAL RUNNABLE SYSTEM (start here)
│       ├── main-system.py        # main entry point
│       ├── best.pt               # trained YOLO button-detection model
│       ├── order_model.pkl       # trained button-ordering model
│       ├── scaler.pkl            # feature scaler for the ordering model
│       ├── features.txt          # ordered feature names used by the model
│       ├── normalize_these.txt   # subset of features to normalize
│       ├── copy-main.js          # JS injected to extract per-button features
│       └── button_ordering_model(1).ipynb  # training notebook
│
├── Button Ordering Module Development Codes/
│   ├── Ordering Part/            # dataset collection + model training (Colab notebooks)
│   └── Semantic Part/            # standalone semantic-similarity experiments
│
├── Integration Testing Codes/    # Selenium test scripts (Navigation, Screenshot, Graph, Other)
│
├── Websites For Demonstration/   # local demo sites used as navigation targets
│   ├── Website 0 / 1 / 2
│   └── web_mapper.py             # crawler used to collect the training dataset
│
└── Web1 Original/                # original demo website source
```

> The runnable system needs its model and config files (`best.pt`, `order_model.pkl`, `scaler.pkl`, `features.txt`, `normalize_these.txt`, `copy-main.js`) to sit **next to `main-system.py`** — they are loaded by relative path.

---

## Prerequisites (System-Level)

Install these on the operating system **before** touching Python.

| Requirement | Why it's needed | How to get it |
|-------------|-----------------|---------------|
| **Python 3.10** | The agent was built/tested on 3.10.2 (pip 23.3.1). 3.10.x recommended. | [python.org/downloads](https://www.python.org/downloads/) — tick "Add Python to PATH" on Windows. |
| **pip** | Installs the Python packages. | Ships with Python. Upgrade: `python -m pip install --upgrade pip`. |
| **Mozilla Firefox** | The agent drives a real Firefox browser via Selenium. | [mozilla.org/firefox](https://www.mozilla.org/firefox/) |
| **geckodriver** | The WebDriver bridge Selenium uses to control Firefox. Must be on your `PATH`. | [geckodriver releases](https://github.com/mozilla/geckodriver/releases) |
| **A desktop GUI session** | `pyautogui` controls the *real* mouse + reads the screen, so this **cannot run headless** or over plain SSH. | Run on a normal desktop (Windows/macOS/Linux with a display). |
| **A static web server** | Demo sites are served locally over HTTP (port `5500`). | VS Code **Live Server** extension, or Python's built-in `http.server` (already included). |
| **Internet (first run only)** | Downloads the `paraphrase-MiniLM-L12-v2` sentence-transformer model (~hundreds of MB). Cached afterwards. | Any connection. |

### Linux extras for `pyautogui`

On Linux, `pyautogui` needs system packages for screen control. Skip on Windows/macOS.

```bash
sudo apt-get install scrot python3-tk python3-dev
```

> ⚠️ **`pyautogui` takes over your physical mouse and keyboard.** While the agent runs it moves your cursor and clicks on screen. Don't use the machine for anything else during a run. `pyautogui.FAILSAFE` is disabled in the code — see [Notes](#notes) to re-enable the corner-abort kill-switch.

---

## Installation

### 1. Get the code

```bash
git clone <your-repo-url>
cd Thesis
```

### 2. Create and activate a virtual environment

Keeps these packages isolated from your system Python.

```bash
# create
python3.10 -m venv venv        # or: python -m venv venv

# activate
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows (PowerShell / CMD)
```

Your prompt should now be prefixed with `(venv)`.

### 3. Upgrade pip (recommended)

```bash
python -m pip install --upgrade pip
```

### 4. Install the Python packages

Either install from the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

…or install them by hand:

```bash
pip install selenium ultralytics pyautogui pandas numpy \
            sentence-transformers networkx matplotlib reportlab
```

#### What each package is for

| Package | Used for |
|---------|----------|
| `selenium` | Drives Firefox, navigates pages, finds DOM links/buttons, takes screenshots. |
| `ultralytics` | Loads/runs the **YOLO** model (`best.pt`) that detects buttons in the screenshot. (Pulls in `torch`, `opencv`, etc. automatically.) |
| `pyautogui` | Human-like mouse movement and clicking on the real screen. |
| `pandas` | Builds the per-button feature DataFrame fed to the ordering model. |
| `numpy` | Math for the curved mouse-motion paths. |
| `sentence-transformers` | Semantic similarity between button text and the target page name. (Pulls in `torch`/`transformers`.) |
| `networkx` | Builds the directed navigation graph. |
| `matplotlib` | Renders the graph image for the report. |
| `reportlab` | Generates the final `report.pdf`. |

> **Standard-library — no install needed:** `time`, `math`, `random`, `io`, `subprocess`, `pickle`.
> Note: the old `README.txt` lists `pip install pickle` — ignore that; `pickle` is built in.

### 5. Install geckodriver

1. Download the build for your OS from the [geckodriver releases](https://github.com/mozilla/geckodriver/releases).
2. Unzip it.
3. Put the `geckodriver` binary somewhere on your `PATH` (e.g. `/usr/local/bin` on Linux/macOS, or any folder added to PATH on Windows) — or simply drop it next to `main-system.py`.
4. Verify: `geckodriver --version`.

### 6. Verify the install

```bash
python -c "import selenium, ultralytics, pyautogui, pandas, numpy, sentence_transformers, networkx, matplotlib, reportlab; print('all imports OK')"
```

If that prints `all imports OK` and `geckodriver --version` works, setup is complete.

---

## Running the System

The agent navigates a **locally served** website. The included demo sites are served best with a static server such as VS Code **Live Server** (default port `5500`).

```bash
# 1. serve the repository (e.g. VS Code Live Server, or:)
python -m http.server 5500

# 2. run the agent from inside its own folder (relative paths matter)
cd "Developed Software/main-system"
python main-system.py
```

The agent opens Firefox, maximizes it, and begins navigating. When done it prints stats and (if enabled) opens `report.pdf`.

### Configuring the target

The current entry point has the URL and target page **hardcoded** in `main()` (`main-system.py`):

```python
url = "http://127.0.0.1:5500/Websites%20For%20Demonstration/Website%202/index.html"
dest_page = "Tuna"
```

To test a different site/target, edit those two lines (or uncomment the `input(...)` prompts already present just above them to enter them interactively).

To enable the PDF report at the end of a run, uncomment the `generate_report(has_found)` call near the bottom of `main()`.

---

## Important: Screen-Coordinate Calibration

The vision-to-click mapping is calibrated for a **1920×1080** display. These constants in `main-system.py` are display-specific and must be adjusted for other resolutions / OS chrome:

```python
MY_SCREEN_X = 1920
MY_SCREEN_Y = 912          # browser viewport height
MY_SCREEN_Y_TABS = 106     # height of browser tab/URL bars
TOTAL_Y_OF_MY_SCREEN = 1080
back_x, back_y = 72, 80     # on-screen position of the browser Back button
```

The pixel scaling in `get_button_identification_coords()` (the `1537` / `732` figures) also assumes this layout. If clicks land in the wrong place, recalibrate these values for your screen and browser.

---

## Supporting Code (not required to run the system)

- **`Button Ordering Module Development Codes/`** — how the ranking model was built: dataset collection from demo sites, feature engineering, and the Colab training notebooks that produced `order_model.pkl` / `scaler.pkl`.
- **`Websites For Demonstration/web_mapper.py`** — crawler that walked the demo sites and exported the per-button feature CSVs used as training data.
- **`Integration Testing Codes/`** — focused Selenium scripts for individual capabilities (manual link navigation, screenshotting, graph rendering).
- **`Button Ordering Module Development Codes/Semantic Part/nlp-test.py`** — standalone sentence-similarity sanity checks.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `geckodriver` not found | Install geckodriver and add it to `PATH`. |
| Clicks miss the buttons | Recalibrate the screen-coordinate constants (see above) for your resolution/browser. |
| `FileNotFoundError` for `features.txt` / `*.pkl` | Run the script from inside `Developed Software/main-system/`; files load by relative path. |
| First run hangs on startup | It's downloading the sentence-transformer model. Wait / check your connection. |
| Cursor moves but nothing useful happens | Make sure the demo site is actually served at the URL in `main()`. |

---

## Notes

- `pyautogui.FAILSAFE` is disabled in the script. Re-enable it (`pyautogui.FAILSAFE = True`) if you want the "slam the mouse to a screen corner to abort" safety kill-switch.
- This is research/thesis code — paths and the target page are hardcoded by design for reproducible demo runs.
