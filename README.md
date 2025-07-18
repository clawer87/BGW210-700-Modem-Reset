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
```
Or add it to your crontab
```bash
crontab -e
```

## Script Behavior:

 * **Checks Internet:** The script will first ping 8.8.8.8 to check if your internet connection is active
 * **Internet Working:** If the internet is working, the script will print a message and exit without doing anything further.
 * **Internet Down:** If the internet is not working, the script will proceed to:
   * Log into your router using the provided password.
   * Initiate a restart of the router.
   * Report success or failure.

## 💡 How It Works (Briefly)

The script leverages the requests library to simulate a web browser's interaction with your router's web interface.
   * It first sends a GET request to the router's homepage and then to the restart.ha page.
   * It parses the HTML response to extract a dynamic nonce value, which is essential for the router's security.
   * It calculates an MD5 hash of your ACCESS_CODE combined with this nonce, mimicking the router's client-side JavaScript.
   * It then sends a POST request with the login credentials to the router's login endpoint.
   * Upon successful login (verified by the presence of the restart form), it extracts a new nonce from the restart page.
   * Finally, it sends another POST request to the restart.ha endpoint with the restart command and the new nonce.
   * Throughout the process, it carefully manages HTTP headers (like Referer and User-Agent) to appear as a legitimate browser.
   * The subprocess module is used to run the system's ping command for internet connectivity checks.

## ⚖️ Disclaimer

Use this script responsibly and at your own risk. Restarting your router will temporarily disrupt your internet connection. Ensure you understand the implications before deploying this in an automated fashion. This script is provided as-is, without warranty of any kind.

## 🙏 Acknowledgments

Special thanks to the Gemini AI assistant for the extensive debugging of this script, as well as for writing this readme!
