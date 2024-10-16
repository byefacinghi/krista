import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def configure_chrome():
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--window-size=1200,699")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    return chrome_options

def login(driver):
    try:
        driver.get("https://web.new.computer/login")
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".email > .sc-7575cab6-4"))
        ).click()

        # Input the email address
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".sc-2c8e1700-12"))
        )
        email_input.send_keys("shafikh.io@icloud.com")

        # Click to submit the email
        driver.find_element(By.CSS_SELECTOR, ".sc-7575cab6-4").click()

        # Input the one-time code manually
        otp = input("Enter the New Computer Email OTP: ")  # Example OTP; in real use, you'd capture this dynamically or input manually

        for i, digit in enumerate(otp):
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, f".sc-2c8e1700-15:nth-child({i+1})"))
            ).send_keys(digit)

        # Move over to the next element (possibly to trigger some JS or visual feedback)
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".sc-2c8e1700-17"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

        print(" ✔ Login successful!")
    except Exception as e:
        print(f" ✘ An error occurred during login: {e}")
        driver.quit()

def logout(driver):
    try:
        # Click on the profile/settings icon
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".sc-8ee6ab41-5 > svg"))
        ).click()

        # Click the logout button
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".btn > .sc-7575cab6-3"))
        ).click()

        print(" ✔ Logout successful!")
    except Exception as e:
        print(f" ✘ An error occurred during logout: {e}")
    finally:
        driver.quit()

def scroll_up_by_amount(driver, delta_y):
    ActionChains(driver)\
        .scroll_by_amount(0, delta_y)\
        .perform()

def scroll_to_top(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll up by a certain amount (negative delta_y for upward scroll)
        scroll_up_by_amount(driver, -5000)  # Adjust -500 to a suitable value

        time.sleep(3)  # Wait for new content to load

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # No new content loaded, we are at the top
            print("Reached the top of the page.")
            break
        last_height = new_height
        print("Scrolling up, waiting for content to load...")

def scrape_content(driver):
    data = []
    try:
        scroll_to_top(driver)  # Scroll to the top to ensure all content is loaded

        # Locate all main response containers
        main_containers = driver.find_elements(By.CSS_SELECTOR, ".sc-8ee6ab41-4.kIBuFv")

        print(f"Found {len(main_containers)} response containers.")

        for container in main_containers:
            response_data = {
                "user_response": "",
                "agent_response": "",
                "sources": [],
                "timestamp": ""
            }

            # Iterate through child elements to categorize
            child_elements = container.find_elements(By.XPATH, "./*")
            for elem in child_elements:
                tag = elem.tag_name.lower()

                if tag == 'div':
                    classes = elem.get_attribute('class').split()
                    if any('sc-ccbb15db-0' in cls for cls in classes):
                        # User response
                        p_tag = elem.find_element(By.TAG_NAME, 'p')
                        response_data["user_response"] = p_tag.text

                    elif any('sc-f6fa4eba-0' in cls for cls in classes):
                        # Agent response
                        if 'sources' not in elem.get_attribute('class'):
                            response_text = elem.text
                            response_data["agent_response"] = response_text

                    elif any('sources' in cls for cls in classes):
                        # Sources/Links
                        links = elem.find_elements(By.TAG_NAME, 'a')
                        for link in links:
                            source_info = {
                                "text": link.text,
                                "href": link.get_attribute("href")
                            }
                            response_data["sources"].append(source_info)

                    elif any('kedlxR' in cls for cls in classes):
                        # Timestamp
                        p_tag = elem.find_element(By.TAG_NAME, 'p')
                        response_data["timestamp"] = p_tag.text

            # Append the collected data for this container if not empty
            if any(response_data.values()):
                data.append(response_data)

        # Optionally sort by timestamp if necessary
        data.sort(key=lambda x: x["timestamp"])

        # Save the data to a JSON file
        with open('scraped_transcript.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Scraping completed. ✔ {len(data)} entries saved to scraped_transcript.json.")
    except Exception as e:
        print(f" ✘ An error occurred during scraping: {e}")

def main():
    driver = webdriver.Chrome(options=configure_chrome())
    try:
        login(driver)  # Perform login
        time.sleep(5)  # Adjust as necessary for post-login content loading

        scrape_content(driver)  # Scrape content after reaching the top

        # Optionally log out
        logout(driver)
    except Exception as e:
        print(f" ✘ An unexpected error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

