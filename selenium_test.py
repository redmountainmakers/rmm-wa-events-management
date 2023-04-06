import os
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def solve_invisible_recaptcha(api_key, site_key, page_url, invisible=1):
    # Submit the initial request to 2captcha
    submit_url = "http://2captcha.com/in.php"
    submit_data = {
        "key": api_key,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": page_url,
        "invisible": invisible,
    }
    response = requests.post(submit_url, data=submit_data)

    print(api_key)

    if not response.text.startswith("OK|"):
        raise ValueError(f"Error submitting captcha: {response.text}")

    captcha_id = response.text.split("|")[1]

    # Poll the 2captcha API for the solution
    result_url = "http://2captcha.com/res.php"
    result_data = {
        "key": api_key,
        "action": "get",
        "id": captcha_id,
    }

    max_retries = 5
    for i in range(max_retries):
        try:
            time.sleep(5 ** i)  # Wait for an exponentially increasing duration
            result = requests.get(result_url, params=result_data)

            if result.text.startswith("OK|"):
                return result.text.split("|")[1]
            elif result.text != "CAPCHA_NOT_READY":
                raise ValueError(f"Error fetching captcha solution: {result.text}")
        except requests.exceptions.RequestException as e:
            if i == max_retries - 1:
                raise e  # Raise the exception if we reached the maximum number of retries

    raise TimeoutError("Timeout reached while waiting for captcha solution")

email = os.environ.get("RMM_EMAIL")
password = os.environ.get("RMM_PASSWORD")
site_key = os.environ.get("SITE_KEY")
api_key = os.environ.get("CAPTCHA_API_KEY")
page_url = "https://redmountainmakers.org/"

file_name = "test.txt"
with open(file_name, "w") as f:
    f.write("This is a test file")

# Set up the mobile browser user agent
mobile_emulation = {
    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
    "userAgent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}

chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

# Add headless and no-sandbox options for running in GitHub Actions
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")

# Set up the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the website and find the login button
driver.get("https://redmountainmakers.org/")
login_button = driver.find_element(By.CSS_SELECTOR, '.mobilePanelButton.buttonLogin')

# Click the login button to reveal the login form
login_button.click()

# Find the username and password fields and fill them in
username_field = driver.find_element(By.ID, "id_QFpB82d_userName")
password_field = driver.find_element(By.ID, "id_QFpB82d_password")
username_field.send_keys(email)
password_field.send_keys(password)

submit_button = driver.find_element(By.ID, "id_QFpB82d_loginAction")
submit_button.click()

solve_invisible_recaptcha(api_key, site_key, page_url)

admin_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.-wa-admin-switcher_admin-view-link')))
admin_button.click()

website_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.-wa-menu-icon[title="Website"]')))
website_button.click()

files_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Files")))
files_button.click()

# Switch to the iframe containing the file browser
iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "idcms_resourceManagement_browser_Frame")))
driver.switch_to.frame(iframe)

expand_files = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ygtvt1 > .ygtvspacer')))
try:
    expand_files.click()
except StaleElementReferenceException:
    # Retry clicking the element if it becomes stale
    expand_files = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ygtvt1 > .ygtvspacer')))
    expand_files.click()

event_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ygtvlabelel5")))
event_button.click()

upload_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.iconUpload')))
upload_button.click()

file_path = Path(file_name).resolve()

file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "file")))
file_input.send_keys(file_path)

ok_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,"ithit_interface_uploadResource_subm_label")))
ok_button.click()


driver.quit()
