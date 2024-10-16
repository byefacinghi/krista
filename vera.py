import re
import sys
import time
import random
import argparse
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from chromedriver_py import binary_path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def parse_usable_proxies():
    """
    Parse the filtered proxies log file and extract usable proxies.
    """
    usable_proxies = []
    usable_proxy_pattern = re.compile(r'Usable Proxy:\s*(\d+\.\d+\.\d+\.\d+:\d+)')

    try:
        with open('proxy/filtered_proxies.txt', 'r') as log_file:
            for line in log_file:
                match = usable_proxy_pattern.search(line)
                if match:
                    usable_proxies.append(match.group(1))
    except FileNotFoundError:
        print("Proxy file not found. Ensure 'proxy/filtered_proxies.txt' exists.")
    except Exception as e:
        print(f"Error reading proxy file: {e}")

    return usable_proxies

def get_random_proxy():
    # Step 1: Parse usable proxies from the log file
    random_proxies = parse_usable_proxies()
    if not random_proxies:
        raise ValueError("No usable proxies found.")
    return random.choice(random_proxies)

def configure_chrome_with_proxy(proxy):
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f'--proxy-server={proxy}')

    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15")
    chrome_options.add_argument("--headless=new")  # Comment out for normal mode
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    return chrome_options

def configure_chrome_without_proxy():
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    # No proxy argument
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15")
    #chrome_options.add_argument("--headless=new")  # Comment out for normal mode
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    return chrome_options

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Selenium Script with Optional Proxy')
    parser.add_argument('--use-proxy', action='store_true', help='Enable proxy usage')
    args = parser.parse_args()

    USE_PROXY = args.use_proxy

    # Select a random proxy if USE_PROXY is True
    if USE_PROXY:
        try:
            selected_proxy = get_random_proxy()
            print(f"Using proxy: {selected_proxy}")
            chrome_options = configure_chrome_with_proxy(selected_proxy)
        except Exception as e:
            print(f"Failed to get proxy: {e}")
            sys.exit(1)
    else:
        print("Proxy is disabled.")
        chrome_options = configure_chrome_without_proxy()

    # Step 1: Set up Selenium WebDriver
    svc = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(options=chrome_options, service=svc)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        """
    })

    try:
        driver.get('https://web.new.computer/login')

        # Step 3: Locate the email input field and submit the email
        email_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@class="sc-2c8e1700-3 fWtYWD email"]'))
        )
        parent_div = driver.find_element(By.XPATH, '//[@class="sc-2c8e1700-6 ekclUc"]')
        email_input = parent_div.find_element(By.XPATH, '//input[@aria-label="Email address"]')

        email_input.send_keys('shafikh.io@icloud.com')
        email_input.send_keys(Keys.RETURN)

        # Wait for the email code input to be ready
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.sc-2c8e1700-15.bbPzXf'))
        )

        # Prompt the user to enter the received email code
        login_code = input("Enter the 6-digit code you received: ").strip()

        # Locate the code input field and submit the code
        code_input = driver.find_element(By.CSS_SELECTOR, 'input.sc-2c8e1700-15.bbPzXf')
        for digit in login_code:
            code_input.send_keys(digit)

        code_input.send_keys(Keys.RETURN)

        # Wait for login to complete (adjust the condition based on actual behavior)
        WebDriverWait(driver, 20).until(
            EC.url_changes('https://web.new.computer/login')  # Adjust based on expected URL after login
        )

        # Capture authentication token from cookies
        cookies = driver.get_cookies()
        auth_token = None
        for cookie in cookies:
            if cookie['name'] == 'auth_token':  # Adjust based on actual token name
                auth_token = cookie['value']
                break

        if auth_token:
            print(f"Authentication successful! Your token is: {auth_token}")
        else:
            print("Token not found in cookies. Check the session manually.")

        # Save cookies for future requests if necessary
        with open("cookies.txt", "w") as file:
            for cookie in cookies:
                file.write(f"{cookie['name']}={cookie['value']}; ")

        # Prompt for logout
        log = input("Logout? (Y/N): ").strip().upper()
        if log == 'Y':
            settings_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Settings"]'))
            )
            settings_button.click()

            # Find the Sign Out button by its class name or by text within the p tag
            sign_out_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.hXJDNG.btn.p.ggjhRJ'))
            )
            sign_out_button.click()
            print("Signed out!")
        elif log == 'N':
            print("Logout Aborted")
        else:
            print("Invalid input. Logout Failed")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

