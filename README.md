# AT&T BGW210-700 Smart Internet Restarter

A Python script designed to automatically check internet connectivity and, if it's down, log into an AT&T BGW210-700 router and initiate a restart. This is particularly useful for headless machines or for setting up automated network maintenance.

## 🚀 Features

* **Internet Connectivity Check:** Pings a reliable external host (`8.8.8.8`) to determine if the internet connection is active.

* **Conditional Restart:** Only attempts to restart the router if the internet connection is detected as down.

* **Automated Login:** Handles the specific login process for AT&T BGW210-700 routers, including nonce extraction and MD5 password hashing.

* **Router Restart Trigger:** Submits the necessary form to initiate a router reboot.

* **Post-Restart Verification:** Waits and confirms that the internet connection has been re-established after a successful restart.

* **Headless Compatible:** Designed to run on servers or devices without a graphical interface.

## 📋 Prerequisites

Before running this script, ensure you have:

* **Python 3.8 or higher** installed on your machine.

* **`pip`** (Python package installer).

## 📦 Installation

1.  **Clone this repository** (or copy the `resetModem.py` file).

2.  **Install the required Python libraries:**

    ```bash
    pip install requests beautifulsoup4
    ```

## 🚀 Usage

To run the script, simply execute it from your terminal:

```bash
python resetModem.py -p password
