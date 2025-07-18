import requests
from bs4 import BeautifulSoup
import urllib.parse
import hashlib
import time
import platform
import subprocess
import sys

parser = argparse.ArgumentParser(description='Logs into a BGW210 router and restarts it')
parser.add_argument('-u', '--url',
                    default='http://192.168.1.254',
                    help='The router remote gateway'
                    )
parser.add_argument('-p', '--password',
                    required=True,
                    help='The router admin password')
args = parser.parse_args()

ROUTER_IP = args.url
ACCESS_CODE = args.password

LOGIN_URL = f"http://{ROUTER_IP}/cgi-bin/login.ha" # The form's action URL
RESTART_URL = f"http://{ROUTER_IP}/cgi-bin/restart.ha" # The URL where the restart form is located

# The router hashes the password prior to submitting the login form
def calculate_md5_hash(text):
    """Calculates the MD5 hash of a given string."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def login_to_router(router_ip, access_code):
    # Use a session, since the router won't let you login without cookies enabled
    session = requests.Session()

    # Set headers, just to make sure it works
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0', # Use your browser's exact User-Agent
        'Referer': f"http://{router_ip}/", # Referer for initial login page GET
        'Accept-Language': 'en-US,en;q=0.5',
    })

    main_page_url = f"http://{router_ip}/" # The URL to hit first
    login_entry_page = f"http://{router_ip}/cgi-bin/restart.ha" # The page where the login form appears if not logged in

    try:
        # 1. Hit the main page first
        print(f"1. Getting main page from {main_page_url}...")
        response_main = session.get(main_page_url)
        response_main.raise_for_status()

        # 2. Hit the page restart page, will show the login form
        print(f"2. Getting login entry page from {login_entry_page} to retrieve nonce...")
        response_login_page = session.get(login_entry_page)
        response_login_page.raise_for_status()

        # print('Cookies after initial GETs: ', session.cookies)

        # We need to grab the nonce tag to combine with the password to create the hashpassword
        soup_login = BeautifulSoup(response_login_page.text, 'html.parser')

        # Check if we are already logged in (if restart form is present)
        restart_form_on_login_page = soup_login.find('form', {'action': '/cgi-bin/restart.ha'})
        if restart_form_on_login_page:
            print("Already logged in. Restart form found on initial page.")
            return session, response_login_page # Return session and the page containing the restart form

        # Find the hidden nonce input field for login
        nonce_tag = soup_login.find('input', {'type': 'hidden', 'name': 'nonce'})
        if not nonce_tag:
            print("Error: Could not find the 'nonce' field on the login page for login.")
            return False, None

        nonce_value = nonce_tag['value']
        print(f"3. Extracted nonce for login: {nonce_value}")

        # 4. Calculate the hashpassword
        combined_string_for_hash = access_code + nonce_value
        hash_password_value = calculate_md5_hash(combined_string_for_hash)
        print(f"4. Calculated hashpassword (MD5 of access_code + nonce): {hash_password_value}")

        masked_password_field = '*' * len(access_code)
        # print(f"4a. Masked password field: {masked_password_field}")

        # 5. Prepare the POST data for login
        login_data = {
            "nonce": nonce_value,
            "password": masked_password_field,
            "hashpassword": hash_password_value,
            "Continue": "Continue"
        }
        # Encode data with windows-1252 as the router seems to expect it
        encoded_data = urllib.parse.urlencode(login_data).encode('windows-1252')

        # 6. POST the login credentials
        print(f"5. Sending POST request to {LOGIN_URL} with login data...")
        # Update Referer to the actual login page for the POST request
        session.headers.update({'Referer': login_entry_page})
        post_response = session.post(LOGIN_URL, data=encoded_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        post_response.raise_for_status()

        # print('Cookies after login POST: ', session.cookies)
        # print(f"Final URL after login POST and redirects: {post_response.url}")
        # print(f"Final status code after login POST: {post_response.status_code}")
        # print(f"Final session cookies after login POST: {session.cookies.get_dict()}")

        # 7. Verify login success by checking the content of the response
        soup_post_login = BeautifulSoup(post_response.text, 'html.parser')
        
        # Check for the presence of the restart form, as that's where the router sends us
        restart_form_after_login = soup_post_login.find('form', {'action': '/cgi-bin/restart.ha'})
        
        if restart_form_after_login:
            print("6. Login successful! Router redirected to the restart page and presented the restart form.")
            return session, post_response # Return session and the page containing the restart form
        else:
            print("6. Login failed. The router did not redirect to the expected restart page or did not show the restart form.")
            print("Response URL:", post_response.url)
            print("Response content snippet (first 1000 chars):")
            print(post_response.text[:1000])
            return False, None

    except requests.exceptions.RequestException as e:
        print(f"An HTTP request error occurred: {e}")
        return False, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False, None

def restart_router(session, restart_page_response):
    print("\n--- Attempting to Restart Router ---")
    soup_restart = BeautifulSoup(restart_page_response.text, 'html.parser')

    # Find the restart form
    restart_form = soup_restart.find('form', {'action': '/cgi-bin/restart.ha', 'method': 'post'})
    if not restart_form:
        print("Error: Could not find the restart form on the page.")
        return False

    # Extract the nonce for the restart form
    nonce_tag_restart = restart_form.find('input', {'type': 'hidden', 'name': 'nonce'})
    if not nonce_tag_restart:
        print("Error: Could not find the 'nonce' field on the restart form.")
        return False

    nonce_value_restart = nonce_tag_restart['value']
    print(f"1. Extracted nonce for restart: {nonce_value_restart}")

    # Prepare the POST data for restart
    restart_data = {
        "nonce": nonce_value_restart,
        "Restart": "Restart" # The value of the Restart button
    }
    encoded_restart_data = urllib.parse.urlencode(restart_data).encode('windows-1252')

    # 2. POST the restart command
    print(f"2. Sending POST request to {RESTART_URL} to restart device...")
    # The Referer should be the page where the restart form was found
    session.headers.update({'Referer': RESTART_URL})
    post_restart_response = session.post(RESTART_URL, data=encoded_restart_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    post_restart_response.raise_for_status()

    # print('Cookies after restart POST: ', session.cookies)
    # print(f"Final URL after restart POST: {post_restart_response.url}")
    # print(f"Final status code after restart POST: {post_restart_response.status_code}")
    # print(f"Response content snippet after restart POST (first 500 chars):\n{post_restart_response.text[:500]}")

    # You might check for a success message or a redirect back to a login page
    # A successful restart often leads to a temporary connection loss or a redirect to a status page.
    if "Restarting" in post_restart_response.text or "/cgi-bin/rebootstatus.ha" in post_restart_response.url:
        print("3. Router restart command sent successfully! Device should be restarting.")
        return True
    else:
        print("3. Restart command might not have been successful or response indicates an issue.")
        return False

def check_internet_connection(target_host="8.8.8.8", timeout_seconds=15):
    """
    Pings a target host to check internet connectivity.
    Returns True if ping is successful, False otherwise.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', target_host]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        print("Error: 'ping' command not found. Please ensure it's installed and in your system's PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during ping check: {e}")
        return False

# --- How to use the function ---
if __name__ == "__main__":
    if check_internet_connection():
        print("Internet is working fine. No modem restart needed.")
    else:
        logged_in_session, restart_page_response = login_to_router(ROUTER_IP, ACCESS_CODE)

        if logged_in_session and restart_page_response:
            print("\nSuccessfully obtained a logged-in session and page with restart form.")
            # Proceed to restart the router
            restart_success = restart_router(logged_in_session, restart_page_response)
            if restart_success:
                print("\nRouter restart process initiated.")
            else:
                print("\nFailed to initiate router restart.")
        else:
            print("\nFailed to login to the router or get the restart page.")