# 🎬 TMDB Mixed Movie Selector & Recommendation Engine

### **CS50x Final Project**
**Author:** DAVID A GRANT  
**Location:** [LONDON, UK]  

---

## 📌 Project Overview
The **TMDB Movie Selector** is an interactive, data-driven web application (and command-line utility) that helps users discover top-rated films tailored to their interests. 

Unlike standard movie recommenders that only fetch basic genre matches, this application leverages custom pooling and backfill algorithms to create a **curated mix** of cinematic options. It merges traditional mainstream blockbusters with niche sub-categories—such as dark comedies, satirical pieces, and retro/indie thrillers—ensuring unique, balanced recommendations every single time.

The project features a complete **separation of concerns**:
* `Movie_selector.py`: A robust analytical backend handling authenticated communication with The Movie Database (TMDB) API, asynchronous pagination pooling, and Pandas DataFrame manipulation.
* `app.py`: A gorgeous, highly responsive visual web dashboard built natively in Python using Streamlit.

Building upon the data manipulation principles learned in Week 5 and the web design frameworks introduced in Week 9, this project transitions from local terminal scripts to an authenticated client-server web architecture..."

"To preserve the defensive programming habits emphasized throughout CS50, the application implements robust exception handling to catch API network drops without compromising user experience...
---

## 🚀 Key Features
* **Secure Authentication:** Eliminates credential leakage vulnerabilities by utilizing secure OS environment variable lookups (`os.environ.get`) for TMDB API Bearer tokens.
#Set up: Windows command:$env:TMDB_READ_ACCESS_TOKEN="your_actual_v4_bearer_token_here"
* **Dynamic UI Controls:** A visual web dashboard with sliding count scales and live-populated selection drop-downs.
* **Algorithmic Content Mixing:** Combines mainstream cinema listings with custom keyword filtering strings (e.g., matching targeted TMDB keyword graphs for Dark Comedy or Suspense).
* **Dynamic Media Rendering:** Asynchronously streams and binds live digital production poster assets directly from TMDB’s Content Delivery Network (CDN) alongside metadata indicators.

---

## 🛠️ Prerequisites & Installation

This application requires Python 3.x and an active internet connection to communicate with the TMDB API endpoints.

# 🛠️ Project Setup and Configuration Guide

Follow these sequential steps to configure your environment variables, install the runtime architecture, and spin up the TMDB Movie Selector application.

---

## 📋 Step 1: Install the Project Dependencies

Before executing the system scripts, you must install the external library packages utilized by the application layout engine. 

Open your system terminal inside the root directory of the project and execute the following installation string:

```bash
pip install streamlit pandas requests

🔑 Step 2: Extract Your TMDB API Read Access Token
The application requires a secure authentication handshake token to pull movie lists and poster art from The Movie Database.

Navigate to your internet browser and log into themoviedb.org.

Hover over your profile icon and click Settings.

Select API from the left navigation column sidebar.

Locate the section labeled API Read Access Token (v4 auth).

Click Copy to copy the entire long alphanumeric token block to your system clipboard.

⚠️ Important: Do not copy the short API Key (v3 auth). The backend architecture specifically expects the long v4 Bearer Token string.

🖥️ Step 3: Configure the OS Environment Variable
To prevent hardcoding secret credentials directly into your codebase, the application pulls your authentication keys using runtime environment scopes.

Identify your operating system environment below and run the corresponding command inside your active VS Code terminal window:

Option A: On Windows (PowerShell)
If your command line prompt begins with PS, run this assignment string:
$env:TMDB_READ_ACCESS_TOKEN="paste_your_copied_long_v4_token_here"
### 1. Clone or Open the Project

Option B: On macOS / Linux / CS50 Codespaces (Bash/Zsh)
If your command line prompt begins with a $, run this export string:
export TMDB_READ_ACCESS_TOKEN="paste_your_copied_long_v4_token_here"
Ensure all project files are situated inside the same working directory:
```text
Movies_Selector/
├── Movie_selector.py   # Backend Logic & Algorithms
├── app.py              # Streamlit Web Application Frontend: To run: [python -m streamlit run app.py]
└── README.md           # Documentation